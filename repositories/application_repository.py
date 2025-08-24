from sqlalchemy.orm import Session
from database.models import Application
from typing import List

def get_applications(db: Session, skip: int = 0, limit: int = 100):
    """Get all active applications with pagination"""
    return db.query(Application).filter(Application.is_active == True).offset(skip).limit(limit).all()

def get_application_by_id(db: Session, app_id: int):
    """Get application by ID"""
    return db.query(Application).filter(Application.id == app_id, Application.is_active == True).first()

def create_application(db: Session, name: str, description: str = None, icon_url: str = None, created_by: int = None):
    """Create a new application"""
    db_app = Application(
        name=name,
        description=description,
        icon_url=icon_url,
        created_by=created_by
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app 