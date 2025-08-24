from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.chat import ChatRequest, ChatResponse
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