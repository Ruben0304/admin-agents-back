"""
Pydantic models for Dynamic Provider management
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class DynamicProviderCreate(BaseModel):
    """Model for creating a new dynamic provider"""
    name: str
    display_name: str
    icon_url: Optional[str] = None
    base_url: Optional[str] = None
    python_code: str
    config_schema: Dict[str, Any]
    required_dependencies: List[str] = []
    validation_code: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Provider name cannot be empty')
        # Only allow alphanumeric and underscores
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Provider name must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower().strip()
    
    @validator('python_code')
    def validate_code(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Python code cannot be empty')
        return v.strip()


class DynamicProviderUpdate(BaseModel):
    """Model for updating an existing dynamic provider"""
    display_name: Optional[str] = None
    icon_url: Optional[str] = None
    base_url: Optional[str] = None
    python_code: Optional[str] = None
    config_schema: Optional[Dict[str, Any]] = None
    required_dependencies: Optional[List[str]] = None
    validation_code: Optional[str] = None
    is_active: Optional[bool] = None


class DynamicProviderResponse(BaseModel):
    """Response model for dynamic provider data"""
    id: int
    name: str
    display_name: str
    icon_url: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool
    is_dynamic: bool
    config_schema: Optional[Dict[str, Any]] = None
    required_dependencies: Optional[List[str]] = None
    has_validation_code: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DynamicProviderCode(BaseModel):
    """Model for provider code operations"""
    python_code: str
    validation_code: Optional[str] = None


class CodeValidationRequest(BaseModel):
    """Request model for code validation"""
    code: str
    validation_code: Optional[str] = None


class CodeValidationResponse(BaseModel):
    """Response model for code validation"""
    is_valid: bool
    message: str
    errors: Optional[List[str]] = None


class CodeTemplateRequest(BaseModel):
    """Request model for code templates"""
    provider_type: str = "openai"


class CodeTemplateResponse(BaseModel):
    """Response model for code templates"""
    provider_type: str
    template: str
    description: str
    required_dependencies: List[str]
    config_schema: Dict[str, Any]


class ProviderTestRequest(BaseModel):
    """Request model for testing dynamic providers"""
    python_code: str
    config_vars: Dict[str, Any]
    test_model: str = "gpt-3.5-turbo"
    test_message: str = "Hello, this is a test message"
    system_prompt: Optional[str] = None


class ProviderTestResponse(BaseModel):
    """Response model for provider testing"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class DynamicProviderConfig(BaseModel):
    """Configuration model for using dynamic providers"""
    provider_name: str
    config_vars: Dict[str, Any]
    
    @validator('config_vars')
    def validate_config_vars(cls, v):
        if 'api_key' not in v:
            raise ValueError('config_vars must include api_key')
        return v


class ProviderDependencyCheck(BaseModel):
    """Model for checking provider dependencies"""
    required_dependencies: List[str]
    
    
class ProviderDependencyResponse(BaseModel):
    """Response for dependency check"""
    available: List[str]
    missing: List[str]
    install_command: Optional[str] = None