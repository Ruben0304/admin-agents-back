from sqlalchemy.orm import Session
from database.models import User
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str, full_name: str = None, is_admin: bool = False):
    """Create a new user with hashed password"""
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_admin=is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str):
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user 