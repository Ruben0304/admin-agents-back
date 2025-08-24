from abc import ABC
from typing import Optional
from providers import chat_with_llm


class BaseAssistant(ABC):
    """
    Base class for all AI assistants.
    Provides common functionality for chatting with LLM providers.
    """
    
    def __init__(self, name: str, llm_provider: str, model: str, 
                 default_system_prompt: str, api_key: Optional[str] = None):
        """
        Initialize the assistant.
        
        Args:
            name: Name of the assistant
            llm_provider: LLM provider name (e.g., 'gemini', 'cohere')
            model: Model name to use
            default_system_prompt: Default system prompt for this assistant
            api_key: Optional API key for the provider
        """
        self.name = name
        self.llm_provider = llm_provider
        self.model = model
        self.default_system_prompt = default_system_prompt
        self.api_key = api_key
    
    async def chat(self, message: str, system_prompt: Optional[str] = None, 
                   streaming: bool = False) -> str:
        """
        Start or continue a conversation with the assistant.
        
        Args:
            message: User message
            system_prompt: Optional system prompt (overrides default if provided)
            streaming: Whether to stream the response
            
        Returns:
            Assistant response
        """
        prompt_to_use = system_prompt if system_prompt is not None else self.default_system_prompt
        
        response = await chat_with_llm(
            provider_name=self.llm_provider,
            model=self.model,
            prompt=message,
            system_prompt=prompt_to_use,
            streaming=streaming,
            api_key=self.api_key
        )
        
        return response
    
    def get_info(self) -> dict:
        """
        Get assistant information.
        
        Returns:
            Dictionary with assistant details
        """
        return {
            "name": self.name,
            "llm_provider": self.llm_provider,
            "model": self.model,
            "default_system_prompt": self.default_system_prompt
        }