from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Application, Provider, Model, Assistant, User, ApiKey
from models.admin import (
    ApplicationCreate, ApplicationResponse,
    ProviderResponse, ModelResponse, ModelCreate,
    AssistantCreate, AssistantResponse, AssistantUpdate,
    UserCreate, UserResponse, ApiKeyCreate, ApiKeyResponse
)
from models.dynamic_provider import (
    DynamicProviderCreate, DynamicProviderUpdate, DynamicProviderResponse,
    DynamicProviderCode, CodeValidationRequest, CodeValidationResponse,
    CodeTemplateRequest, CodeTemplateResponse, ProviderTestRequest, ProviderTestResponse
)
from models.dynamic_application import (
    ApplicationTemplateCreate, ApplicationTemplateResponse, ApplicationFromTemplate, ApplicationCreatedResponse,
    AssistantTemplateCreate, AssistantTemplateResponse, AssistantFromTemplate, AssistantCreatedResponse,
    TemplatePreviewRequest, TemplatePreviewResponse
)
from services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from passlib.context import CryptContext
from providers.llm_factory import LLMFactory
from providers.dynamic_provider import dynamic_provider_manager
import time
import asyncio

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_data = AuthService.verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_data

def get_admin_user(current_user = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Applications CRUD
@router.get("/applications", response_model=List[ApplicationResponse])
def list_applications(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Application).filter(Application.is_active == True).all()

@router.post("/applications", response_model=ApplicationResponse)
def create_application(app: ApplicationCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    db_app = Application(
        name=app.name,
        description=app.description,
        icon_url=app.icon_url,
        endpoint=app.endpoint,
        created_by=current_user["user_id"]
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

# Application Templates CRUD (must come before generic application routes to avoid path conflicts)
@router.get("/applications/templates", response_model=List[ApplicationTemplateResponse])
def list_application_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """List all application templates, optionally filtered by category"""
    from repositories import get_application_templates, get_application_templates_by_category
    
    if category:
        templates = get_application_templates_by_category(db, category)
    else:
        templates = get_application_templates(db)
    
    return templates

@router.post("/applications/templates", response_model=ApplicationTemplateResponse)
def create_application_template(
    template: ApplicationTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new application template (admin only)"""
    from repositories import create_application_template
    
    try:
        db_template = create_application_template(db, template, current_user["id"])
        return db_template
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications/templates/{template_id}", response_model=ApplicationTemplateResponse)
def get_application_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific application template"""
    from repositories import get_application_template_by_id
    
    template = get_application_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Application template not found")
    
    return template

@router.post("/applications/from-template", response_model=ApplicationCreatedResponse)
def create_application_from_template(
    request: ApplicationFromTemplate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create application and assistants from template"""
    from repositories import create_application_from_template, get_application_template_by_id
    
    try:
        template = get_application_template_by_id(db, request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        application, assistants = create_application_from_template(db, request, current_user["id"])
        
        assistants_data = [
            {
                "id": asst.id,
                "name": asst.name,
                "endpoint": asst.endpoint,
                "description": asst.description
            }
            for asst in assistants
        ]
        
        return ApplicationCreatedResponse(
            application_id=application.id,
            application_name=application.name,
            endpoint=application.endpoint,
            assistants_created=assistants_data,
            template_used=template.name,
            message=f"Application '{application.name}' created successfully with {len(assistants)} assistants"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    app = db.query(Application).filter(Application.id == app_id, Application.is_active == True).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# Providers CRUD
@router.get("/providers", response_model=List[ProviderResponse])
def list_providers(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Provider).filter(Provider.is_active == True).all()

# Dynamic Providers (must come before generic provider routes)
@router.get("/providers/dynamic", response_model=List[DynamicProviderResponse])
def list_dynamic_providers(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """List all dynamic providers"""
    providers = db.query(Provider).filter(
        Provider.is_dynamic == True, 
        Provider.is_active == True
    ).all()
    
    responses = []
    for provider in providers:
        response = DynamicProviderResponse(
            id=provider.id,
            name=provider.name,
            display_name=provider.display_name,
            icon_url=provider.icon_url,
            base_url=provider.base_url,
            is_active=provider.is_active,
            is_dynamic=provider.is_dynamic,
            config_schema=provider.config_schema or {},
            required_dependencies=provider.required_dependencies or [],
            has_validation_code=bool(provider.validation_code),
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
        responses.append(response)
    
    return responses

@router.get("/providers/{provider_id}", response_model=ProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    provider = db.query(Provider).filter(Provider.id == provider_id, Provider.is_active == True).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

# Models CRUD
@router.get("/models", response_model=List[ModelResponse])
def list_models(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Model).filter(Model.is_active == True).all()

@router.get("/providers/{provider_id}/models", response_model=List[ModelResponse])
def list_provider_models(provider_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Model).filter(Model.provider_id == provider_id, Model.is_active == True).all()

@router.get("/models/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    model = db.query(Model).filter(Model.id == model_id, Model.is_active == True).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@router.post("/models", response_model=ModelResponse)
def create_model(model: ModelCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    db_model = Model(
        name=model.name,
        display_name=model.display_name,
        provider_id=model.provider_id,
        max_tokens=model.max_tokens,
        supports_streaming=model.supports_streaming,
        supports_system_prompt=model.supports_system_prompt,
        cost_per_token=model.cost_per_token
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

# Assistant Templates CRUD (must come before generic assistant routes to avoid path conflicts)
@router.get("/assistants/templates", response_model=List[AssistantTemplateResponse])
def list_assistant_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all assistant templates, optionally filtered by category"""
    from repositories import get_assistant_templates, get_assistant_templates_by_category
    
    if category:
        templates = get_assistant_templates_by_category(db, category)
    else:
        templates = get_assistant_templates(db)
    
    return templates

@router.post("/assistants/templates", response_model=AssistantTemplateResponse)
def create_assistant_template(
    template: AssistantTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Create a new assistant template (admin only)"""
    from repositories import create_assistant_template
    
    try:
        db_template = create_assistant_template(db, template, current_user["id"])
        return db_template
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assistants/templates/{template_id}", response_model=AssistantTemplateResponse)
def get_assistant_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific assistant template"""
    from repositories import get_assistant_template_by_id
    
    template = get_assistant_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Assistant template not found")
    
    return template

@router.post("/assistants/from-template", response_model=AssistantCreatedResponse)
def create_assistant_from_template(
    request: AssistantFromTemplate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create assistant from template"""
    from repositories import create_assistant_from_template, get_assistant_template_by_id
    
    try:
        template = get_assistant_template_by_id(db, request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        assistant = create_assistant_from_template(db, request, current_user["id"])
        
        # Get resolved system prompt preview (first 200 chars)
        system_prompt_preview = assistant.system_prompt[:200] + "..." if len(assistant.system_prompt) > 200 else assistant.system_prompt
        
        return AssistantCreatedResponse(
            assistant_id=assistant.id,
            assistant_name=assistant.name,
            endpoint=assistant.endpoint,
            application_name=assistant.application.name,
            template_used=template.name,
            system_prompt_preview=system_prompt_preview,
            message=f"Assistant '{assistant.name}' created successfully from template '{template.name}'"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Assistants CRUD
@router.get("/assistants", response_model=List[AssistantResponse])
def list_assistants(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Assistant).filter(Assistant.is_active == True).all()

@router.get("/applications/{app_id}/assistants", response_model=List[AssistantResponse])
def list_application_assistants(app_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Assistant).filter(Assistant.application_id == app_id, Assistant.is_active == True).all()

@router.get("/assistants/{assistant_id}", response_model=AssistantResponse)
def get_assistant(assistant_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assistant = db.query(Assistant).filter(Assistant.id == assistant_id, Assistant.is_active == True).first()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistant

@router.post("/assistants", response_model=AssistantResponse)
def create_assistant(assistant: AssistantCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_assistant = Assistant(
        name=assistant.name,
        description=assistant.description,
        system_prompt=assistant.system_prompt,
        application_id=assistant.application_id,
        model_id=assistant.model_id,
        api_key=assistant.api_key,
        is_streaming=assistant.is_streaming,
        config=assistant.config,
        endpoint=assistant.endpoint,
        created_by=current_user["user_id"]
    )
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    return db_assistant

@router.put("/assistants/{assistant_id}", response_model=AssistantResponse)
def update_assistant(assistant_id: int, assistant_update: AssistantUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_assistant = db.query(Assistant).filter(Assistant.id == assistant_id, Assistant.is_active == True).first()
    if not db_assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    
    update_data = assistant_update.dict(exclude_none=True)
    for key, value in update_data.items():
        setattr(db_assistant, key, value)
    
    db.commit()
    db.refresh(db_assistant)
    return db_assistant

# Users CRUD
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    # Check if user already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# API Keys CRUD
@router.get("/providers/{provider_id}/api-keys", response_model=List[ApiKeyResponse])
def list_provider_api_keys(provider_id: int, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    return db.query(ApiKey).filter(ApiKey.provider_id == provider_id, ApiKey.is_active == True).all()

@router.post("/api-keys", response_model=ApiKeyResponse)
def create_api_key(api_key: ApiKeyCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    encrypted_key = f"encrypted_{api_key.key}"  # Placeholder encryption
    db_api_key = ApiKey(
        name=api_key.name,
        provider_id=api_key.provider_id,
        encrypted_key=encrypted_key,
        created_by=current_user["user_id"]
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

# Dynamic Providers CRUD

@router.post("/providers/dynamic/debug")
async def debug_dynamic_provider(request: Request):
    """Debug endpoint to see raw request data"""
    body = await request.body()
    print(f"Raw request body: {body.decode('utf-8')}")
    try:
        import json
        json_data = json.loads(body.decode('utf-8'))
        print(f"Parsed JSON keys: {list(json_data.keys())}")
        for key, value in json_data.items():
            print(f"  {key}: {type(value)} = {str(value)[:100]}...")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
    return {"message": "Debug info logged"}

@router.post("/providers/dynamic", response_model=DynamicProviderResponse)
def create_dynamic_provider(
    provider: DynamicProviderCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_admin_user)
):
    """Create a new dynamic provider with custom Python code"""
    
    # Debug logging
    print(f"Received provider data:")
    print(f"  name: {getattr(provider, 'name', 'MISSING')}")
    print(f"  display_name: {getattr(provider, 'display_name', 'MISSING')}")
    print(f"  python_code: {getattr(provider, 'python_code', 'MISSING')[:100] if hasattr(provider, 'python_code') else 'MISSING'}...")
    print(f"  config_schema: {getattr(provider, 'config_schema', 'MISSING')}")
    print(f"  required_dependencies: {getattr(provider, 'required_dependencies', 'MISSING')}")
    
    print(f"Creating dynamic provider: {provider.name}")
    print(f"Display name: {provider.display_name}")
    print(f"Config schema: {provider.config_schema}")
    
    # Validate the Python code first
    try:
        is_valid, error_message = LLMFactory.validate_dynamic_provider_code(provider.python_code)
        if not is_valid:
            print(f"Code validation failed: {error_message}")
            raise HTTPException(
                status_code=400, 
                detail=f"Code validation failed: {error_message}"
            )
    except Exception as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
    
    # Check if provider name already exists
    existing_provider = db.query(Provider).filter(Provider.name == provider.name).first()
    if existing_provider:
        print(f"Provider name already exists: {provider.name}")
        raise HTTPException(status_code=400, detail="Provider name already exists")
    
    # Create the dynamic provider
    try:
        db_provider = Provider(
            name=provider.name,
            display_name=provider.display_name,
            icon_url=provider.icon_url,
            base_url=provider.base_url,
            is_dynamic=True,
            python_code=provider.python_code,
            config_schema=provider.config_schema,
            required_dependencies=provider.required_dependencies,
            validation_code=provider.validation_code
        )
        print(f"Created provider object: {db_provider.name}")
    except Exception as e:
        print(f"Error creating provider object: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating provider: {str(e)}")
    
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    
    # Register the provider in the factory
    LLMFactory.register_dynamic_provider(provider.name, {
        'name': provider.name,
        'display_name': provider.display_name,
        'python_code': provider.python_code,
        'config_schema': provider.config_schema,
        'required_dependencies': provider.required_dependencies,
        'validation_code': provider.validation_code,
    })
    
    # Return response with has_validation_code field
    response = DynamicProviderResponse(
        id=db_provider.id,
        name=db_provider.name,
        display_name=db_provider.display_name,
        icon_url=db_provider.icon_url,
        base_url=db_provider.base_url,
        is_active=db_provider.is_active,
        is_dynamic=db_provider.is_dynamic,
        config_schema=db_provider.config_schema or {},
        required_dependencies=db_provider.required_dependencies or [],
        has_validation_code=bool(db_provider.validation_code),
        created_at=db_provider.created_at,
        updated_at=db_provider.updated_at
    )
    
    return response


@router.get("/providers/dynamic/{provider_id}", response_model=DynamicProviderResponse)
def get_dynamic_provider(
    provider_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Get a specific dynamic provider"""
    provider = db.query(Provider).filter(
        Provider.id == provider_id,
        Provider.is_dynamic == True,
        Provider.is_active == True
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Dynamic provider not found")
    
    response = DynamicProviderResponse(
        id=provider.id,
        name=provider.name,
        display_name=provider.display_name,
        icon_url=provider.icon_url,
        base_url=provider.base_url,
        is_active=provider.is_active,
        is_dynamic=provider.is_dynamic,
        config_schema=provider.config_schema or {},
        required_dependencies=provider.required_dependencies or [],
        has_validation_code=bool(provider.validation_code),
        created_at=provider.created_at,
        updated_at=provider.updated_at
    )
    
    return response

@router.put("/providers/dynamic/{provider_id}", response_model=DynamicProviderResponse)
def update_dynamic_provider(
    provider_id: int,
    provider_update: DynamicProviderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Update a dynamic provider"""
    db_provider = db.query(Provider).filter(
        Provider.id == provider_id,
        Provider.is_dynamic == True,
        Provider.is_active == True
    ).first()
    
    if not db_provider:
        raise HTTPException(status_code=404, detail="Dynamic provider not found")
    
    # If updating Python code, validate it first
    if provider_update.python_code is not None:
        is_valid, error_message = LLMFactory.validate_dynamic_provider_code(provider_update.python_code)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Code validation failed: {error_message}"
            )
    
    # Update the provider
    update_data = provider_update.dict(exclude_none=True)
    for key, value in update_data.items():
        setattr(db_provider, key, value)
    
    db.commit()
    db.refresh(db_provider)
    
    # Re-register in factory if code was updated
    if provider_update.python_code is not None or provider_update.config_schema is not None:
        LLMFactory.register_dynamic_provider(db_provider.name, {
            'name': db_provider.name,
            'display_name': db_provider.display_name,
            'python_code': db_provider.python_code,
            'config_schema': db_provider.config_schema,
            'required_dependencies': db_provider.required_dependencies,
            'validation_code': db_provider.validation_code,
        })
    
    response = DynamicProviderResponse(
        id=db_provider.id,
        name=db_provider.name,
        display_name=db_provider.display_name,
        icon_url=db_provider.icon_url,
        base_url=db_provider.base_url,
        is_active=db_provider.is_active,
        is_dynamic=db_provider.is_dynamic,
        config_schema=db_provider.config_schema or {},
        required_dependencies=db_provider.required_dependencies or [],
        has_validation_code=bool(db_provider.validation_code),
        created_at=db_provider.created_at,
        updated_at=db_provider.updated_at
    )
    
    return response

@router.get("/providers/dynamic/{provider_id}/code", response_model=DynamicProviderCode)
def get_provider_code(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Get the Python code for a dynamic provider (admin only for security)"""
    provider = db.query(Provider).filter(
        Provider.id == provider_id,
        Provider.is_dynamic == True,
        Provider.is_active == True
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Dynamic provider not found")
    
    return DynamicProviderCode(
        python_code=provider.python_code or "",
        validation_code=provider.validation_code
    )

@router.post("/providers/code/validate", response_model=CodeValidationResponse)
def validate_provider_code(
    request: CodeValidationRequest,
    current_user = Depends(get_admin_user)
):
    """Validate Python code for dynamic providers"""
    is_valid, message = LLMFactory.validate_dynamic_provider_code(request.code)
    
    # Also validate the validation code if provided
    validation_errors = []
    if request.validation_code:
        is_val_valid, val_message = LLMFactory.validate_dynamic_provider_code(request.validation_code)
        if not is_val_valid:
            validation_errors.append(f"Validation code error: {val_message}")
    
    return CodeValidationResponse(
        is_valid=is_valid and len(validation_errors) == 0,
        message=message,
        errors=validation_errors if validation_errors else None
    )

@router.get("/providers/code/template", response_model=CodeTemplateResponse)
def get_code_template(
    request: CodeTemplateRequest = Depends(),
    current_user = Depends(get_admin_user)
):
    """Get a code template for creating dynamic providers"""
    template_code = LLMFactory.get_code_template(request.provider_type)
    
    # Define template metadata
    templates_info = {
        "openai": {
            "description": "Template for OpenAI GPT models integration",
            "dependencies": ["openai"],
            "config": {
                "api_key": {"type": "string", "required": True, "description": "OpenAI API key"},
                "max_tokens": {"type": "integer", "default": 1000, "description": "Maximum tokens per response"},
                "temperature": {"type": "float", "default": 0.7, "description": "Sampling temperature"}
            }
        },
        "anthropic": {
            "description": "Template for Anthropic Claude models integration",
            "dependencies": ["anthropic"],
            "config": {
                "api_key": {"type": "string", "required": True, "description": "Anthropic API key"},
                "max_tokens": {"type": "integer", "default": 1000, "description": "Maximum tokens per response"}
            }
        }
    }
    
    info = templates_info.get(request.provider_type, templates_info["openai"])
    
    return CodeTemplateResponse(
        provider_type=request.provider_type,
        template=template_code,
        description=info["description"],
        required_dependencies=info["dependencies"],
        config_schema=info["config"]
    )

@router.post("/providers/dynamic/test", response_model=ProviderTestResponse)
async def test_dynamic_provider(
    request: ProviderTestRequest,
    current_user = Depends(get_admin_user)
):
    """Test a dynamic provider configuration"""
    try:
        start_time = time.time()
        
        # Validate the code first
        is_valid, error_message = LLMFactory.validate_dynamic_provider_code(request.python_code)
        if not is_valid:
            return ProviderTestResponse(
                success=False,
                error=f"Code validation failed: {error_message}"
            )
        
        # Create a temporary dynamic provider
        test_provider = dynamic_provider_manager.create_provider_from_db(
            {
                "name": "test_provider",
                "python_code": request.python_code
            },
            request.config_vars
        )
        
        # Test the provider
        response = await test_provider.chat(
            model=request.test_model,
            prompt=request.test_message,
            system_prompt=request.system_prompt,
            streaming=False
        )
        
        execution_time = time.time() - start_time
        
        return ProviderTestResponse(
            success=True,
            response=response,
            execution_time=execution_time
        )
        
    except Exception as e:
        return ProviderTestResponse(
            success=False,
            error=str(e)
        )

@router.delete("/providers/dynamic/{provider_id}")
def delete_dynamic_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """Soft delete a dynamic provider"""
    provider = db.query(Provider).filter(
        Provider.id == provider_id,
        Provider.is_dynamic == True
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Dynamic provider not found")
    
    provider.is_active = False
    db.commit()
    
    return {"message": "Dynamic provider deleted successfully"}


# ============ TEMPLATE UTILITIES ENDPOINTS ============

@router.post("/templates/preview", response_model=TemplatePreviewResponse)
def preview_template(
    request: TemplatePreviewRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Preview template with variables resolved"""
    from repositories import (
        get_application_template_by_id, get_assistant_template_by_id,
        preview_template_with_variables
    )
    
    try:
        if request.template_type == "application":
            template = get_application_template_by_id(db, request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Application template not found")
            
            # Preview application data
            preview_data = {
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "category": template.category,
                "default_assistants": template.default_assistants
            }
            
            return TemplatePreviewResponse(
                preview_data=preview_data,
                resolved_config=template.template_config
            )
            
        elif request.template_type == "assistant":
            template = get_assistant_template_by_id(db, request.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Assistant template not found")
            
            # Resolve system prompt with variables
            resolved_prompt = preview_template_with_variables(
                template.system_prompt_template, 
                request.variables
            )
            
            preview_data = {
                "name": template.name,
                "display_name": template.display_name,
                "description": template.description,
                "category": template.category,
                "default_provider": template.default_provider,
                "default_model": template.default_model,
                "prompt_variables": template.prompt_variables
            }
            
            return TemplatePreviewResponse(
                preview_data=preview_data,
                resolved_system_prompt=resolved_prompt,
                resolved_config=template.default_config
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid template_type. Must be 'application' or 'assistant'")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/categories")
def get_template_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available template categories"""
    from repositories import get_template_categories
    
    return get_template_categories(db)


@router.get("/templates/search")
def search_templates(
    q: str,
    template_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search templates by query string"""
    from repositories import search_application_templates, search_assistant_templates
    
    results = {}
    
    if not template_type or template_type == "application":
        results["application_templates"] = search_application_templates(db, q)
    
    if not template_type or template_type == "assistant":
        results["assistant_templates"] = search_assistant_templates(db, q)
    
    return results