from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Application, Provider, Model, Assistant, User, ApiKey
from models.admin import (
    ApplicationCreate, ApplicationResponse,
    ProviderResponse, ModelResponse, ModelCreate,
    AssistantCreate, AssistantResponse, AssistantUpdate,
    UserCreate, UserResponse, ApiKeyCreate, ApiKeyResponse
)
from services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from passlib.context import CryptContext

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