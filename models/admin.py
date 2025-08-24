from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    endpoint: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon_url: Optional[str]
    is_active: bool
    endpoint: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

class ProviderCreate(BaseModel):
    name: str
    display_name: str
    icon_url: Optional[str] = None
    base_url: Optional[str] = None

class ProviderResponse(BaseModel):
    id: int
    name: str
    display_name: str
    icon_url: Optional[str]
    base_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class ModelCreate(BaseModel):
    name: str
    display_name: str
    provider_id: int
    max_tokens: Optional[int] = None
    supports_streaming: bool = True
    supports_system_prompt: bool = True
    cost_per_token: Optional[str] = None

class ModelResponse(BaseModel):
    id: int
    name: str
    display_name: str
    provider_id: int
    max_tokens: Optional[int]
    supports_streaming: bool
    supports_system_prompt: bool
    cost_per_token: Optional[str]
    is_active: bool
    provider: Optional[ProviderResponse]
    created_at: datetime
    updated_at: Optional[datetime]

class AssistantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    application_id: int
    model_id: int
    api_key: Optional[str] = None
    is_streaming: bool = True
    config: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None

class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[int] = None
    api_key: Optional[str] = None
    is_streaming: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None

class AssistantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    system_prompt: str
    application_id: int
    model_id: int
    api_key: Optional[str]
    is_streaming: bool
    is_active: bool
    config: Optional[Dict[str, Any]]
    endpoint: Optional[str] = None
    application: Optional[ApplicationResponse]
    model: Optional[ModelResponse]
    created_at: datetime
    updated_at: Optional[datetime]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]

class ApiKeyCreate(BaseModel):
    name: str
    provider_id: int
    key: str

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    provider_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]