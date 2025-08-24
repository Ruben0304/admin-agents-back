from sqlalchemy.orm import Session
from database.models import Provider
from typing import List

def get_all_providers(db: Session):
    """Get all active providers"""
    return db.query(Provider).filter(Provider.is_active == True).all()

def get_provider_by_name(db: Session, name: str):
    """Get provider by name"""
    return db.query(Provider).filter(Provider.name == name, Provider.is_active == True).first()

def get_provider_by_id(db: Session, provider_id: int):
    """Get provider by ID"""
    return db.query(Provider).filter(Provider.id == provider_id, Provider.is_active == True).first()

def create_new_provider(db: Session, name: str, display_name: str, icon_url: str = None, base_url: str = None):
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