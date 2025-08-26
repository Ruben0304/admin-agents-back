from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    system_prompt: Optional[str] = None
    streaming: bool = False
    api_key: Optional[str] = None
    config_vars: Optional[Dict[str, Any]] = None  # For dynamic providers

class AssistantChatRequest(BaseModel):
    prompt: str
    streaming: Optional[bool] = None  # Override assistant's default streaming setting

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str

class AssistantChatResponse(BaseModel):
    response: str
    assistant_name: str
    provider: str
    model: str
    streaming_used: bool