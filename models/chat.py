from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"
    system_prompt: Optional[str] = None
    streaming: bool = False
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str