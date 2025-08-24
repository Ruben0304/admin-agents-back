from typing import Optional
from ..base_assistant import BaseAssistant


class Suncar(BaseAssistant):
    """
    Suncar assistant for automotive services, car maintenance, and vehicle advice.
    """
    
    def __init__(self, llm_provider: str, model: str, api_key: Optional[str] = None):
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
            api_key=api_key
        )