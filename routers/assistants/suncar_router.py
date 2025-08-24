from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.database import get_db
from repositories import *
from models.chat import AssistantChatRequest, AssistantChatResponse
from providers import chat_with_llm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import AuthService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/suncar", tags=["Suncar Assistant"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    token = credentials.credentials
    user_data = AuthService.verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_data

@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_suncar(
    request: AssistantChatRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Chat with Suncar automotive assistant.
    This endpoint loads Suncar's configuration from the database.
    """
    try:
        # Get Suncar assistant from database by name
        assistant = get_assistant_by_name(db, "Suncar")
        if not assistant:
            raise HTTPException(status_code=404, detail="Suncar assistant not found")
        
        if not assistant.is_active:
            raise HTTPException(status_code=400, detail="Suncar assistant is not active")
        
        # Get the model and provider information
        model = assistant.model
        provider = model.provider
        
        # Get API key (from assistant or provider's api_keys)
        api_key = assistant.api_key
        if not api_key:
            # Get provider's default API key
            api_keys = get_api_keys_by_provider(db, provider.id)
            if api_keys:
                # Use first active API key (in real app, decrypt it)
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Chat with LLM using Suncar's configuration from database
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=request.prompt,
            system_prompt=assistant.system_prompt,
            streaming=assistant.is_streaming,
            api_key=api_key
        )
        
        return AssistantChatResponse(
            response=response,
            assistant_name=assistant.name,
            provider=provider.display_name,
            model=model.display_name,
            streaming_used=assistant.is_streaming
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_suncar_info(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get Suncar assistant information and configuration"""
    try:
        assistant = get_assistant_by_name(db, "Suncar")
        if not assistant:
            raise HTTPException(status_code=404, detail="Suncar assistant not found")
        
        return {
            "assistant_name": assistant.name,
            "description": assistant.description,
            "system_prompt": assistant.system_prompt,
            "model": assistant.model.display_name,
            "provider": assistant.model.provider.display_name,
            "streaming_enabled": assistant.is_streaming,
            "is_active": assistant.is_active,
            "created_at": assistant.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 