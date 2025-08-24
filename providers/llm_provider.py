from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator

class LLMProvider(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = self._get_api_key(api_key)
        self._initialize_client()
    
    @abstractmethod
    def _get_api_key(self, provided_key: Optional[str]) -> str:
        """Get API key from parameter or environment variable"""
        pass
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the specific LLM client"""
        pass
    
    @abstractmethod
    async def chat(self, model: str, prompt: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        """Generate chat response with optional streaming"""
        pass
    
    @abstractmethod
    async def _chat_streaming(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate streaming chat response"""
        pass
    
    @abstractmethod
    async def _chat_sync(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate synchronous chat response"""
        pass