from typing import Optional
from ..base_assistant import BaseAssistant
from sqlalchemy.orm import Session


class MoneyTracker(BaseAssistant):
    """
    MoneyTracker assistant for personal finance management and budgeting advice.
    Can be initialized with direct parameters or loaded from database.
    """
    
    def __init__(self, llm_provider: str = None, model: str = None, api_key: Optional[str] = None,
                 assistant_id: Optional[int] = None, db: Optional[Session] = None,
                 streaming: Optional[bool] = None):
        """
        Initialize MoneyTracker assistant.
        
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
            default_prompt = """You are MoneyTracker, a personal finance assistant specialized in:
- Budget planning and expense tracking
- Financial goal setting and monitoring
- Investment advice for beginners
- Saving strategies and tips
- Debt management guidance
- Financial education and literacy

You provide practical, actionable advice to help users manage their money effectively.
Be encouraging, clear, and always emphasize responsible financial practices."""
            
            super().__init__(
                name="MoneyTracker",
                llm_provider=llm_provider,
                model=model,
                default_system_prompt=default_prompt,
                api_key=api_key,
                streaming=streaming
            )