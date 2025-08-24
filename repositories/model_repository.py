from sqlalchemy.orm import Session
from database.models import Model
from typing import List

def get_models_by_provider(db: Session, provider_id: int):
    """Get all active models for a specific provider"""
    return db.query(Model).filter(Model.provider_id == provider_id, Model.is_active == True).all()

def get_model_by_id(db: Session, model_id: int):
    """Get model by ID"""
    return db.query(Model).filter(Model.id == model_id, Model.is_active == True).first()

def create_model(db: Session, name: str, display_name: str, provider_id: int, max_tokens: int = None, 
                supports_streaming: bool = True, supports_system_prompt: bool = True, cost_per_token: str = None):
    """Create a new model"""
    db_model = Model(
        name=name,
        display_name=display_name,
        provider_id=provider_id,
        max_tokens=max_tokens,
        supports_streaming=supports_streaming,
        supports_system_prompt=supports_system_prompt,
        cost_per_token=cost_per_token
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model 