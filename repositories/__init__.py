# Repositories package
from .user_repository import *
from .application_repository import *
from .provider_repository import *
from .model_repository import *
from .assistant_repository import *
from .api_key_repository import *
from .template_repository import *

__all__ = [
    # User operations
    "get_user_by_username",
    "get_user_by_email", 
    "create_user",
    "verify_password",
    "authenticate_user",
    
    # Application operations
    "get_all_applications",
    "get_application_by_id",
    "create_new_application",
    
    # Provider operations
    "get_all_providers",
    "get_provider_by_name",
    "get_provider_by_id",
    "create_new_provider",
    
    # Model operations
    "get_models_by_provider",
    "get_model_by_id",
    "create_model",
    
    # Assistant operations
    "get_assistants_by_application",
    "get_assistant_by_id",
    "get_assistant_by_name",
    "create_assistant",
    "update_assistant",
    
    # API Key operations
    "get_api_keys_by_provider",
    "create_api_key",
    
    # Template operations
    "get_application_templates",
    "get_application_template_by_id",
    "get_application_templates_by_category",
    "create_application_template",
    "create_application_from_template",
    "get_assistant_templates",
    "get_assistant_template_by_id",
    "get_assistant_templates_by_category",
    "create_assistant_template",
    "create_assistant_from_template",
    "extract_template_variables",
    "preview_template_with_variables",
    "search_application_templates",
    "search_assistant_templates",
    "get_template_categories"
]