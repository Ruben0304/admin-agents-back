from models.auth import LoginRequest, LoginResponse
from repositories import authenticate_user
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os


SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def authenticate_user_db(db: Session, credentials: LoginRequest) -> LoginResponse:
        user = authenticate_user(db, credentials.username, credentials.password)
        if user:
            access_token = AuthService.create_access_token(
                data={"sub": user.username, "user_id": user.id, "is_admin": user.is_admin}
            )
            return LoginResponse(
                token=access_token,
                message="Login successful",
                user_id=user.id,
                username=user.username,
                is_admin=user.is_admin
            )
        else:
            return LoginResponse(
                token="",
                message="Invalid credentials"
            )

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            is_admin: bool = payload.get("is_admin", False)
            if username is None:
                return None
            return {"username": username, "user_id": user_id, "is_admin": is_admin}
        except JWTError:
            return None