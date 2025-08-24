from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.auth import LoginRequest, LoginResponse
from services.auth_service import AuthService
from database.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.authenticate_user_db(db, credentials)