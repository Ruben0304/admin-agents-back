from fastapi import APIRouter
from models.auth import LoginRequest, LoginResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    return AuthService.authenticate_user(credentials)