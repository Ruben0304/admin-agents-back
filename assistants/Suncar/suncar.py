from typing import Optional
from ..base_assistant import BaseAssistant
from sqlalchemy.orm import Session


class Suncar(BaseAssistant):
    """
    Suncar assistant for automotive services, car maintenance, and vehicle advice.
    Can be initialized with direct parameters or loaded from database.
    """
    
    def __init__(self, llm_provider: str = None, model: str = None, api_key: Optional[str] = None,
                 assistant_id: Optional[int] = None, db: Optional[Session] = None,
                 streaming: Optional[bool] = None):
        """
        Initialize Suncar assistant.
        
        Args:
            llm_provider: LLM provider name (if not loading from DB)
            model: Model name (if not loading from DB)
            api_key: API key (if not loading from DB)
            assistant_id: Assistant ID to load from database
            db: Database session (required if using assistant_id)
            streaming: Whether to use streaming (if not loading from DB)
        """
        if assistant_id and db:
            # Load from database
            super().__init__(assistant_id=assistant_id, db=db)
        else:
            # Initialize with direct parameters
            default_prompt = """You are Suncar, an automotive expert assistant specialized in:
- Vehicle maintenance schedules and reminders
- Car troubleshooting and diagnostic advice
- Automotive repair guidance
- Vehicle purchasing recommendations
- Fuel efficiency tips and driving advice
- Car care and cleaning tips
- Auto insurance and warranty guidance

You provide reliable, practical automotive advice to help users maintain their vehicles properly.
Be knowledgeable, safety-focused, and always recommend professional service when needed."""
            
            super().__init__(
                name="Suncar",
                llm_provider=llm_provider,
                model=model,
                default_system_prompt=default_prompt,
                api_key=api_key,
                streaming=streaming
            )