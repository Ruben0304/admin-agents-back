from abc import ABC
from typing import Optional
from providers import chat_with_llm
from repositories import *
from sqlalchemy.orm import Session


class BaseAssistant(ABC):
    """
    Base class for all AI assistants.
    Provides common functionality for chatting with LLM providers.
    Can be initialized with direct parameters or loaded from database.
    """
    
    def __init__(self, name: str = None, llm_provider: str = None, model: str = None, 
                 default_system_prompt: str = None, api_key: Optional[str] = None,
                 assistant_id: Optional[int] = None, db: Optional[Session] = None,
                 streaming: Optional[bool] = None):
        """
        Initialize the assistant either with direct parameters or from database.
        
        Args:
            name: Name of the assistant
            llm_provider: LLM provider name (e.g., 'gemini', 'cohere')
            model: Model name to use
            default_system_prompt: Default system prompt for this assistant
            api_key: Optional API key for the provider
            assistant_id: Optional assistant ID to load from database
            db: Database session (required if using assistant_id)
            streaming: Whether to use streaming (loaded from DB if assistant_id provided)
        """
        if assistant_id and db:
            self._load_from_database(assistant_id, db)
        else:
            self.name = name
            self.llm_provider = llm_provider
            self.model = model
            self.default_system_prompt = default_system_prompt
            self.api_key = api_key
            self.streaming = streaming if streaming is not None else False
            self.assistant_id = None
    
    def _load_from_database(self, assistant_id: int, db: Session):
        """Load assistant configuration from database."""
        assistant = crud.get_assistant_by_id(db, assistant_id)
        if not assistant:
            raise ValueError(f"Assistant with ID {assistant_id} not found")
        
        if not assistant.is_active:
            raise ValueError(f"Assistant with ID {assistant_id} is not active")
        
        self.assistant_id = assistant.id
        self.name = assistant.name
        self.default_system_prompt = assistant.system_prompt
        self.streaming = assistant.is_streaming
        
        # Get provider and model information
        model = assistant.model
        provider = model.provider
        self.llm_provider = provider.name
        self.model = model.name
        
        # Get API key
        self.api_key = assistant.api_key
        if not self.api_key:
            # Get provider's default API key
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                # Use first active API key (in real app, decrypt it)
                self.api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
    
    @classmethod
    def from_database(cls, assistant_id: int, db: Session):
        """
        Create an assistant instance loading all configuration from database.
        
        Args:
            assistant_id: ID of the assistant to load
            db: Database session
            
        Returns:
            BaseAssistant instance with configuration loaded from database
        """
        return cls(assistant_id=assistant_id, db=db)
    
    async def chat(self, message: str, system_prompt: Optional[str] = None, 
                   streaming: Optional[bool] = None) -> str:
        """
        Start or continue a conversation with the assistant.
        
        Args:
            message: User message
            system_prompt: Optional system prompt (overrides default if provided)
            streaming: Optional streaming override (uses assistant's DB config if None)
            
        Returns:
            Assistant response
        """
        prompt_to_use = system_prompt if system_prompt is not None else self.default_system_prompt
        streaming_to_use = streaming if streaming is not None else self.streaming
        
        response = await chat_with_llm(
            provider_name=self.llm_provider,
            model=self.model,
            prompt=message,
            system_prompt=prompt_to_use,
            streaming=streaming_to_use,
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