from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    endpoint = Column(String(100), unique=True, nullable=True)  # API endpoint for this application
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User")
    assistants = relationship("Assistant", back_populates="application")

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    icon_url = Column(String(255))
    base_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Dynamic Provider Fields
    is_dynamic = Column(Boolean, default=False)  # True for user-created providers
    python_code = Column(Text)  # Python code template for provider implementation
    required_dependencies = Column(JSON)  # List of pip packages needed
    config_schema = Column(JSON)  # Schema for configuration variables (API keys, endpoints, etc.)
    validation_code = Column(Text)  # Code to validate configuration and API keys
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    models = relationship("Model", back_populates="provider")

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    display_name = Column(String(150), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    max_tokens = Column(Integer)
    supports_streaming = Column(Boolean, default=True)
    supports_system_prompt = Column(Boolean, default=True)
    cost_per_token = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    provider = relationship("Provider", back_populates="models")
    assistants = relationship("Assistant", back_populates="model")

class Assistant(Base):
    __tablename__ = "assistants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id"))
    model_id = Column(Integer, ForeignKey("models.id"))
    api_key = Column(String(255))  # Optional API key override
    endpoint = Column(String(100), nullable=True)  # API endpoint for this assistant
    is_streaming = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    config = Column(JSON)  # Additional configuration as JSON
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    application = relationship("Application", back_populates="assistants")
    model = relationship("Model", back_populates="assistants")
    creator = relationship("User")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    provider = relationship("Provider")
    creator = relationship("User")


class ApplicationTemplate(Base):
    __tablename__ = "application_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(150), nullable=False)
    description = Column(Text)
    icon_url = Column(String(255))
    category = Column(String(50), default="general")
    tags = Column(JSON, default=list)  # List of tags
    template_config = Column(JSON, default=dict)  # Configuration template
    default_assistants = Column(JSON, default=list)  # Default assistants configuration
    usage_count = Column(Integer, default=0)  # How many times this template was used
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User")


class AssistantTemplate(Base):
    __tablename__ = "assistant_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="general")
    system_prompt_template = Column(Text, nullable=False)  # System prompt with variables like {company_name}
    default_provider = Column(String(50))  # Default provider name
    default_model = Column(String(100))    # Default model name
    default_config = Column(JSON, default=dict)  # Default configuration
    tags = Column(JSON, default=list)  # List of tags
    prompt_variables = Column(JSON, default=list)  # Variables that can be customized
    usage_count = Column(Integer, default=0)  # How many times this template was used
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User")