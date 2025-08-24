from sqlalchemy.orm import Session
from database.models import Provider
from typing import List

def get_providers(db: Session, skip: int = 0, limit: int = 100):
    """Get all active providers with pagination"""
    return db.query(Provider).filter(Provider.is_active == True).offset(skip).limit(limit).all()

def get_provider_by_name(db: Session, name: str):
    """Get provider by name"""
    return db.query(Provider).filter(Provider.name == name, Provider.is_active == True).first()

def create_provider(db: Session, name: str, display_name: str, icon_url: str = None, base_url: str = None):
    """Create a new provider"""
    db_provider = Provider(
        name=name,
        display_name=display_name,
        icon_url=icon_url,
        base_url=base_url
    )
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider 