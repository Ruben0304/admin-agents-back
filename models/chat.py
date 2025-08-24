from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    system_prompt: Optional[str] = None
    streaming: bool = False
    api_key: Optional[str] = None

class AssistantChatRequest(BaseModel):
    assistant_id: int
    message: str

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