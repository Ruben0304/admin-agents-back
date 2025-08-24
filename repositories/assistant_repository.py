from sqlalchemy.orm import Session
from database.models import Assistant
from typing import List

def get_assistants_by_application(db: Session, application_id: int):
    """Get all active assistants for a specific application"""
    return db.query(Assistant).filter(Assistant.application_id == application_id, Assistant.is_active == True).all()

def get_assistant_by_id(db: Session, assistant_id: int):
    """Get assistant by ID"""
    return db.query(Assistant).filter(Assistant.id == assistant_id, Assistant.is_active == True).first()

def get_assistant_by_name(db: Session, name: str):
    """Get assistant by name"""
    return db.query(Assistant).filter(Assistant.name == name, Assistant.is_active == True).first()

def create_assistant(db: Session, name: str, system_prompt: str, application_id: int, model_id: int,
                    description: str = None, api_key: str = None, is_streaming: bool = True, 
                    config: dict = None, created_by: int = None):
    """Create a new assistant"""
    db_assistant = Assistant(
        name=name,
        description=description,
        system_prompt=system_prompt,
        application_id=application_id,
        model_id=model_id,
        api_key=api_key,
        is_streaming=is_streaming,
        config=config,
        created_by=created_by
    )
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    return db_assistant

def update_assistant(db: Session, assistant_id: int, **kwargs):
    """Update assistant with provided fields"""
    db_assistant = get_assistant_by_id(db, assistant_id)
    if db_assistant:
        for key, value in kwargs.items():
            if hasattr(db_assistant, key):
                setattr(db_assistant, key, value)
        db.commit()
        db.refresh(db_assistant)
    return db_assistant 