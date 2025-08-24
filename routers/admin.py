from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from repositories import *
from models.admin import (
    ApplicationCreate, ApplicationResponse,
    ProviderResponse, ModelResponse, ModelCreate,
    AssistantCreate, AssistantResponse, AssistantUpdate,
    UserCreate, UserResponse, ApiKeyCreate, ApiKeyResponse
)
from services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

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

# Applications endpoints
@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_applications(db, skip=skip, limit=limit)

@router.post("/applications", response_model=ApplicationResponse)
def create_application(app: ApplicationCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    return crud.create_application(
        db=db,
        name=app.name,
        description=app.description,
        icon_url=app.icon_url,
        created_by=current_user["user_id"]
    )

@router.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    app = crud.get_application_by_id(db, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# Providers endpoints
@router.get("/providers", response_model=List[ProviderResponse])
def get_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_providers(db, skip=skip, limit=limit)

@router.get("/providers/{provider_id}/models", response_model=List[ModelResponse])
def get_provider_models(provider_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_models_by_provider(db, provider_id)

@router.post("/models", response_model=ModelResponse)
def create_model(model: ModelCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    return crud.create_model(
        db=db,
        name=model.name,
        display_name=model.display_name,
        provider_id=model.provider_id,
        max_tokens=model.max_tokens,
        supports_streaming=model.supports_streaming,
        supports_system_prompt=model.supports_system_prompt,
        cost_per_token=model.cost_per_token
    )

# Assistants endpoints
@router.get("/applications/{app_id}/assistants", response_model=List[AssistantResponse])
def get_application_assistants(app_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.get_assistants_by_application(db, app_id)

@router.post("/assistants", response_model=AssistantResponse)
def create_assistant(assistant: AssistantCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.create_assistant(
        db=db,
        name=assistant.name,
        description=assistant.description,
        system_prompt=assistant.system_prompt,
        application_id=assistant.application_id,
        model_id=assistant.model_id,
        api_key=assistant.api_key,
        is_streaming=assistant.is_streaming,
        config=assistant.config,
        created_by=current_user["user_id"]
    )

@router.get("/assistants/{assistant_id}", response_model=AssistantResponse)
def get_assistant(assistant_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    assistant = crud.get_assistant_by_id(db, assistant_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistant

@router.put("/assistants/{assistant_id}", response_model=AssistantResponse)
def update_assistant(assistant_id: int, assistant_update: AssistantUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Convert Pydantic model to dict, excluding None values
    update_data = assistant_update.dict(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    updated_assistant = crud.update_assistant(db, assistant_id, **update_data)
    if not updated_assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return updated_assistant

# User management endpoints
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    # Check if user already exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    return crud.create_user(
        db=db,
        username=user.username,
        email=user.email,
        password=user.password,
        full_name=user.full_name,
        is_admin=user.is_admin
    )

# API Keys endpoints (encrypted storage)
@router.get("/providers/{provider_id}/api-keys", response_model=List[ApiKeyResponse])
def get_provider_api_keys(provider_id: int, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    return crud.get_api_keys_by_provider(db, provider_id)

@router.post("/api-keys", response_model=ApiKeyResponse)
def create_api_key(api_key: ApiKeyCreate, db: Session = Depends(get_db), current_user = Depends(get_admin_user)):
    # In a real implementation, you would encrypt the API key before storing
    encrypted_key = f"encrypted_{api_key.key}"  # Placeholder encryption
    return crud.create_api_key(
        db=db,
        name=api_key.name,
        provider_id=api_key.provider_id,
        encrypted_key=encrypted_key,
        created_by=current_user["user_id"]
    )