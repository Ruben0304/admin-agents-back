from typing import Optional
from ..base_assistant import BaseAssistant


class MoneyTracker(BaseAssistant):
    """
    MoneyTracker assistant for personal finance management and budgeting advice.
    """
    
    def __init__(self, llm_provider: str, model: str, api_key: Optional[str] = None):
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
            api_key=api_key
        )