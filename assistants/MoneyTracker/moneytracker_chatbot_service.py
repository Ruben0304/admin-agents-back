from typing import Optional, Dict, Any
from .moneytracker import MoneyTracker


class MoneyTrackerChatbotService:
    """
    Service class for MoneyTracker chatbot functionality.
    Handles conversation management and specialized money tracking features.
    """
    
    def __init__(self, llm_provider: str, model: str, api_key: Optional[str] = None):
        self.assistant = MoneyTracker(llm_provider, model, api_key)
        self.conversation_history = []
    
    async def chat(self, message: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        """
        Process a chat message with MoneyTracker assistant.
        
        Args:
            message: User message
            system_prompt: Optional custom system prompt (overrides default)
            streaming: Whether to stream the response
            
        Returns:
            Assistant response
        """
        response = await self.assistant.chat(message, system_prompt, streaming)
        
        # Store conversation history
        self.conversation_history.append({
            "user": message,
            "assistant": response,
            "timestamp": self._get_timestamp()
        })
        
        return response
    
    async def get_budget_advice(self, income: float, expenses: Dict[str, float]) -> str:
        """
        Get personalized budget advice based on income and expenses.
        
        Args:
            income: Monthly income
            expenses: Dictionary of expense categories and amounts
            
        Returns:
            Budget analysis and recommendations
        """
        expense_breakdown = "\n".join([f"- {category}: ${amount}" for category, amount in expenses.items()])
        total_expenses = sum(expenses.values())
        
        message = f"""Please analyze my budget:
        
Monthly Income: ${income}
Monthly Expenses:
{expense_breakdown}

Total Expenses: ${total_expenses}
Remaining: ${income - total_expenses}

Please provide a detailed budget analysis with recommendations for improvement."""
        
        return await self.chat(message)
    
    async def get_saving_plan(self, goal: str, target_amount: float, timeframe_months: int) -> str:
        """
        Create a saving plan for a specific financial goal.
        
        Args:
            goal: Description of the saving goal
            target_amount: Target amount to save
            timeframe_months: Number of months to achieve the goal
            
        Returns:
            Detailed saving plan
        """
        monthly_target = target_amount / timeframe_months
        
        message = f"""Help me create a saving plan:
        
Goal: {goal}
Target Amount: ${target_amount}
Timeframe: {timeframe_months} months
Monthly Saving Needed: ${monthly_target:.2f}

Please provide a detailed saving strategy and tips to achieve this goal."""
        
        return await self.chat(message)
    
    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()