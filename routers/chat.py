from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.chat import ChatRequest, ChatResponse, AssistantChatRequest, AssistantChatResponse
from providers import chat_with_llm
from database.database import get_db
from repositories import *

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_with_llm(
            provider_name=request.provider,
            model=request.model,
            prompt=request.message,
            system_prompt=request.system_prompt,
            streaming=request.streaming,
            api_key=request.api_key
        )
        
        return ChatResponse(
            response=response,
            provider=request.provider,
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assistant", response_model=AssistantChatResponse)
async def chat_with_assistant(request: AssistantChatRequest, db: Session = Depends(get_db)):
    try:
        # Get assistant from database with all its configuration
        assistant = crud.get_assistant_by_id(db, request.assistant_id)
        if not assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")
        
        if not assistant.is_active:
            raise HTTPException(status_code=400, detail="Assistant is not active")
        
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
        
        # Chat with LLM using assistant's configuration from database
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

@router.get("/test")
async def test_gemini():
    try:
        response = await chat_with_llm(
            provider_name="gemini",
            model="gemini-2.5-pro",
            prompt="¿Cuál es tu función principal?",
            system_prompt="Eres un asistente especializado en desarrollo de software.",
            streaming=False
        )
        
        return {
            "message": "Test successful",
            "response": response,
            "provider": "gemini",
            "model": "gemini-2.5-pro"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))