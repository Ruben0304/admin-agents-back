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
        assistant = crud.get_assistant_by_name(db, "Suncar")
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
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                # Use first active API key (in real app, decrypt it)
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Chat with LLM using Suncar's configuration from database
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=request.message,
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
        assistant = crud.get_assistant_by_name(db, "Suncar")
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

@router.post("/maintenance-schedule")
async def get_maintenance_schedule(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get vehicle maintenance schedule using Suncar's specialized knowledge.
    This is a specialized endpoint for automotive maintenance.
    """
    try:
        # Get Suncar assistant
        assistant = crud.get_assistant_by_name(db, "Suncar")
        if not assistant:
            raise HTTPException(status_code=404, detail="Suncar assistant not found")
        
        # Create specialized prompt for maintenance schedule
        maintenance_prompt = f"""
        As a specialized automotive assistant, provide a detailed maintenance schedule for:
        Vehicle: {request.get('vehicle_make', 'Unknown')} {request.get('vehicle_model', 'Unknown')}
        Year: {request.get('year', 'Unknown')}
        Mileage: {request.get('current_mileage', 'Unknown')}
        
        Please provide:
        1. Immediate maintenance needs
        2. 3-month schedule
        3. 6-month schedule
        4. Annual maintenance items
        5. Cost estimates for each service
        """
        
        # Get model and provider info
        model = assistant.model
        provider = model.provider
        
        # Get API key
        api_key = assistant.api_key
        if not api_key:
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Get maintenance schedule from LLM
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=maintenance_prompt,
            system_prompt=assistant.system_prompt,
            streaming=False,
            api_key=api_key
        )
        
        return {
            "maintenance_schedule": response,
            "vehicle_info": request,
            "generated_at": datetime.now().isoformat(),
            "assistant": "Suncar"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/diagnose-problem")
async def diagnose_vehicle_problem(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Diagnose vehicle problems using Suncar's automotive expertise.
    This is a specialized endpoint for vehicle diagnostics.
    """
    try:
        # Get Suncar assistant
        assistant = crud.get_assistant_by_name(db, "Suncar")
        if not assistant:
            raise HTTPException(status_code=404, detail="Suncar assistant not found")
        
        # Create specialized prompt for problem diagnosis
        diagnosis_prompt = f"""
        As a specialized automotive diagnostic assistant, analyze this vehicle problem:
        
        Symptoms: {request.get('symptoms', 'No symptoms provided')}
        Vehicle: {request.get('vehicle_make', 'Unknown')} {request.get('vehicle_model', 'Unknown')}
        Year: {request.get('year', 'Unknown')}
        Mileage: {request.get('current_mileage', 'Unknown')}
        Problem Description: {request.get('problem_description', 'No description provided')}
        
        Please provide:
        1. Most likely causes (ranked by probability)
        2. Diagnostic steps to confirm
        3. Estimated repair costs
        4. Urgency level (immediate, soon, can wait)
        5. DIY vs professional repair recommendations
        """
        
        # Get model and provider info
        model = assistant.model
        provider = model.provider
        
        # Get API key
        api_key = assistant.api_key
        if not api_key:
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Get diagnosis from LLM
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=diagnosis_prompt,
            system_prompt=assistant.system_prompt,
            streaming=False,
            api_key=api_key
        )
        
        return {
            "diagnosis": response,
            "vehicle_info": request,
            "diagnosed_at": datetime.now().isoformat(),
            "assistant": "Suncar"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 