"""
Repository functions for application and assistant templates
"""
from sqlalchemy.orm import Session
from database.models import ApplicationTemplate, AssistantTemplate, Application, Assistant
from models.dynamic_application import (
    ApplicationTemplateCreate, AssistantTemplateCreate,
    ApplicationFromTemplate, AssistantFromTemplate
)
from typing import List, Optional
import string
import re


def get_application_templates(db: Session) -> List[ApplicationTemplate]:
    """Get all active application templates"""
    return db.query(ApplicationTemplate).filter(ApplicationTemplate.is_active == True).all()


def get_application_template_by_id(db: Session, template_id: int) -> Optional[ApplicationTemplate]:
    """Get application template by ID"""
    return db.query(ApplicationTemplate).filter(
        ApplicationTemplate.id == template_id,
        ApplicationTemplate.is_active == True
    ).first()


def get_application_templates_by_category(db: Session, category: str) -> List[ApplicationTemplate]:
    """Get application templates by category"""
    return db.query(ApplicationTemplate).filter(
        ApplicationTemplate.category == category,
        ApplicationTemplate.is_active == True
    ).all()


def create_application_template(db: Session, template: ApplicationTemplateCreate, user_id: int) -> ApplicationTemplate:
    """Create a new application template"""
    db_template = ApplicationTemplate(
        name=template.name,
        display_name=template.display_name,
        description=template.description,
        icon_url=template.icon_url,
        category=template.category,
        tags=template.tags,
        template_config=template.template_config,
        default_assistants=template.default_assistants,
        created_by=user_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def create_application_from_template(
    db: Session, 
    request: ApplicationFromTemplate, 
    user_id: int
) -> tuple[Application, List[Assistant]]:
    """Create application and assistants from template"""
    # Get template
    template = get_application_template_by_id(db, request.template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Generate endpoint if not provided
    endpoint = request.custom_endpoint
    if not endpoint:
        endpoint = f"/api/{request.application_name.lower().replace(' ', '-').replace('_', '-')}"
    
    # Create application
    application = Application(
        name=request.application_name,
        description=request.description or template.description,
        icon_url=template.icon_url,
        endpoint=endpoint,
        created_by=user_id
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Create assistants if requested
    assistants_created = []
    if request.create_default_assistants and template.default_assistants:
        for assistant_config in template.default_assistants:
            # Apply customizations if provided
            customization = next(
                (c for c in request.assistant_customizations 
                 if c.get('name') == assistant_config.get('name')), 
                {}
            )
            
            assistant = Assistant(
                name=customization.get('name', assistant_config.get('name')),
                description=customization.get('description', assistant_config.get('description')),
                system_prompt=customization.get('system_prompt', assistant_config.get('system_prompt')),
                application_id=application.id,
                model_id=customization.get('model_id', assistant_config.get('model_id')),
                endpoint=customization.get('endpoint', assistant_config.get('endpoint')),
                is_streaming=customization.get('is_streaming', assistant_config.get('is_streaming', True)),
                config=customization.get('config', assistant_config.get('config', {})),
                created_by=user_id
            )
            db.add(assistant)
            assistants_created.append(assistant)
    
    if assistants_created:
        db.commit()
        for assistant in assistants_created:
            db.refresh(assistant)
    
    # Update template usage count
    template.usage_count += 1
    db.commit()
    
    return application, assistants_created


def get_assistant_templates(db: Session) -> List[AssistantTemplate]:
    """Get all active assistant templates"""
    return db.query(AssistantTemplate).filter(AssistantTemplate.is_active == True).all()


def get_assistant_template_by_id(db: Session, template_id: int) -> Optional[AssistantTemplate]:
    """Get assistant template by ID"""
    return db.query(AssistantTemplate).filter(
        AssistantTemplate.id == template_id,
        AssistantTemplate.is_active == True
    ).first()


def get_assistant_templates_by_category(db: Session, category: str) -> List[AssistantTemplate]:
    """Get assistant templates by category"""
    return db.query(AssistantTemplate).filter(
        AssistantTemplate.category == category,
        AssistantTemplate.is_active == True
    ).all()


def create_assistant_template(db: Session, template: AssistantTemplateCreate, user_id: int) -> AssistantTemplate:
    """Create a new assistant template"""
    db_template = AssistantTemplate(
        name=template.name,
        display_name=template.display_name,
        description=template.description,
        category=template.category,
        system_prompt_template=template.system_prompt_template,
        default_provider=template.default_provider,
        default_model=template.default_model,
        default_config=template.default_config,
        tags=template.tags,
        prompt_variables=template.prompt_variables,
        created_by=user_id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def create_assistant_from_template(
    db: Session, 
    request: AssistantFromTemplate, 
    user_id: int
) -> Assistant:
    """Create assistant from template"""
    # Get template
    template = get_assistant_template_by_id(db, request.template_id)
    if not template:
        raise ValueError("Template not found")
    
    # Resolve system prompt variables
    system_prompt = template.system_prompt_template
    if request.prompt_variables:
        for var, value in request.prompt_variables.items():
            system_prompt = system_prompt.replace(f"{{{var}}}", value)
    
    # Use custom system prompt if provided
    if request.custom_system_prompt:
        system_prompt = request.custom_system_prompt
    
    # Generate endpoint if not provided
    endpoint = request.custom_endpoint
    if not endpoint:
        endpoint = f"/assistants/{request.assistant_name.lower().replace(' ', '-').replace('_', '-')}"
    
    # Merge configurations
    config = template.default_config.copy()
    config.update(request.custom_config)
    
    # Create assistant
    assistant = Assistant(
        name=request.assistant_name,
        description=template.description,
        system_prompt=system_prompt,
        application_id=request.application_id,
        model_id=request.model_id,
        endpoint=endpoint,
        config=config,
        created_by=user_id
    )
    db.add(assistant)
    db.commit()
    db.refresh(assistant)
    
    # Update template usage count
    template.usage_count += 1
    db.commit()
    
    return assistant


def extract_template_variables(template_text: str) -> List[str]:
    """Extract variables from template text (format: {variable_name})"""
    pattern = r'\{([^}]+)\}'
    variables = re.findall(pattern, template_text)
    return list(set(variables))


def preview_template_with_variables(template_text: str, variables: dict) -> str:
    """Preview template with variables resolved"""
    result = template_text
    for var, value in variables.items():
        result = result.replace(f"{{{var}}}", str(value))
    return result


def search_application_templates(db: Session, query: str) -> List[ApplicationTemplate]:
    """Search application templates by name, display_name, or tags"""
    search_term = f"%{query}%"
    return db.query(ApplicationTemplate).filter(
        ApplicationTemplate.is_active == True,
        (
            ApplicationTemplate.name.ilike(search_term) |
            ApplicationTemplate.display_name.ilike(search_term) |
            ApplicationTemplate.description.ilike(search_term)
        )
    ).all()


def search_assistant_templates(db: Session, query: str) -> List[AssistantTemplate]:
    """Search assistant templates by name, display_name, or tags"""
    search_term = f"%{query}%"
    return db.query(AssistantTemplate).filter(
        AssistantTemplate.is_active == True,
        (
            AssistantTemplate.name.ilike(search_term) |
            AssistantTemplate.display_name.ilike(search_term) |
            AssistantTemplate.description.ilike(search_term)
        )
    ).all()


def get_template_categories(db: Session) -> dict:
    """Get available categories for both templates"""
    app_categories = db.query(ApplicationTemplate.category).filter(
        ApplicationTemplate.is_active == True
    ).distinct().all()
    
    assistant_categories = db.query(AssistantTemplate.category).filter(
        AssistantTemplate.is_active == True
    ).distinct().all()
    
    return {
        'application_categories': [cat[0] for cat in app_categories],
        'assistant_categories': [cat[0] for cat in assistant_categories]
    }