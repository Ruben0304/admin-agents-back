"""
Pydantic models for Dynamic Application management
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class ApplicationTemplateCreate(BaseModel):
    """Model for creating a new application template"""
    name: str
    display_name: str
    description: str
    icon_url: Optional[str] = None
    category: str = "general"
    tags: List[str] = []
    template_config: Dict[str, Any] = {}
    default_assistants: List[Dict[str, Any]] = []
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Application name cannot be empty')
        # Only allow alphanumeric, spaces, underscores, and hyphens
        if not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('Application name must contain only alphanumeric characters, spaces, underscores, and hyphens')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = [
            'ecommerce', 'banking', 'healthcare', 'education', 
            'customer_support', 'sales', 'marketing', 'hr', 
            'legal', 'real_estate', 'automotive', 'general'
        ]
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v


class ApplicationFromTemplate(BaseModel):
    """Model for creating application from template"""
    template_id: int
    application_name: str
    description: Optional[str] = None
    custom_endpoint: Optional[str] = None
    create_default_assistants: bool = True
    assistant_customizations: List[Dict[str, Any]] = []
    
    @validator('application_name')
    def validate_application_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Application name cannot be empty')
        return v.strip()


class ApplicationTemplateResponse(BaseModel):
    """Response model for application template"""
    id: int
    name: str
    display_name: str
    description: str
    icon_url: Optional[str] = None
    category: str
    tags: List[str]
    template_config: Dict[str, Any]
    default_assistants: List[Dict[str, Any]]
    usage_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ApplicationCreatedResponse(BaseModel):
    """Response when application is created from template"""
    application_id: int
    application_name: str
    endpoint: Optional[str] = None
    assistants_created: List[Dict[str, Any]] = []
    template_used: str
    message: str


class AssistantTemplateCreate(BaseModel):
    """Model for creating assistant templates"""
    name: str
    display_name: str
    description: str
    category: str = "general"
    system_prompt_template: str
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    default_config: Dict[str, Any] = {}
    tags: List[str] = []
    prompt_variables: List[str] = []  # Variables that can be customized in system prompt
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Assistant template name cannot be empty')
        return v.strip()
    
    @validator('category')
    def validate_category(cls, v):
        allowed_categories = [
            'customer_support', 'sales', 'technical_support', 'content_writing',
            'data_analysis', 'translation', 'education', 'healthcare',
            'legal', 'financial', 'marketing', 'hr', 'general'
        ]
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v


class AssistantFromTemplate(BaseModel):
    """Model for creating assistant from template"""
    template_id: int
    assistant_name: str
    application_id: int
    provider_id: Optional[int] = None
    model_id: Optional[int] = None
    custom_system_prompt: Optional[str] = None
    prompt_variables: Dict[str, str] = {}
    custom_endpoint: Optional[str] = None
    custom_config: Dict[str, Any] = {}
    
    @validator('assistant_name')
    def validate_assistant_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Assistant name cannot be empty')
        return v.strip()


class AssistantTemplateResponse(BaseModel):
    """Response model for assistant template"""
    id: int
    name: str
    display_name: str
    description: str
    category: str
    system_prompt_template: str
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    default_config: Dict[str, Any]
    tags: List[str]
    prompt_variables: List[str]
    usage_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AssistantCreatedResponse(BaseModel):
    """Response when assistant is created from template"""
    assistant_id: int
    assistant_name: str
    endpoint: Optional[str] = None
    application_name: str
    template_used: str
    system_prompt_preview: str
    message: str


class TemplatePreviewRequest(BaseModel):
    """Request for previewing template with variables"""
    template_id: int
    template_type: str  # 'application' or 'assistant'
    variables: Dict[str, str] = {}


class TemplatePreviewResponse(BaseModel):
    """Response for template preview"""
    preview_data: Dict[str, Any]
    resolved_system_prompt: Optional[str] = None
    resolved_config: Dict[str, Any] = {}