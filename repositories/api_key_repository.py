from sqlalchemy.orm import Session
from database.models import ApiKey
from typing import List

def get_api_keys_by_provider(db: Session, provider_id: int):
    """Get all active API keys for a specific provider"""
    return db.query(ApiKey).filter(ApiKey.provider_id == provider_id, ApiKey.is_active == True).all()

def create_api_key(db: Session, name: str, provider_id: int, encrypted_key: str, created_by: int):
    """Create a new API key"""
    db_api_key = ApiKey(
        name=name,
        provider_id=provider_id,
        encrypted_key=encrypted_key,
        created_by=created_by
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key 