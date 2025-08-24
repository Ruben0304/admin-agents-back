from typing import Optional, Dict, Any
from .suncar import Suncar


class SuncarChatbotService:
    """
    Service class for Suncar chatbot functionality.
    Handles conversation management and specialized automotive features.
    """
    
    def __init__(self, llm_provider: str, model: str, api_key: Optional[str] = None):
        self.assistant = Suncar(llm_provider, model, api_key)
        self.conversation_history = []
        self.vehicle_profile = {}
    
    async def chat(self, message: str, system_prompt: Optional[str] = None, streaming: bool = False) -> str:
        """
        Process a chat message with Suncar assistant.
        
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
    
    async def get_maintenance_schedule(self, vehicle_info: Dict[str, Any]) -> str:
        """
        Get maintenance schedule based on vehicle information.
        
        Args:
            vehicle_info: Dictionary containing vehicle details (make, model, year, mileage)
            
        Returns:
            Maintenance schedule recommendations
        """
        self.vehicle_profile.update(vehicle_info)
        
        message = f"""Please provide a maintenance schedule for my vehicle:
        
Make: {vehicle_info.get('make', 'Unknown')}
Model: {vehicle_info.get('model', 'Unknown')}
Year: {vehicle_info.get('year', 'Unknown')}
Current Mileage: {vehicle_info.get('mileage', 'Unknown')}

Please include upcoming maintenance items and their recommended intervals."""
        
        return await self.chat(message)
    
    async def diagnose_problem(self, symptoms: str, vehicle_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Help diagnose vehicle problems based on symptoms.
        
        Args:
            symptoms: Description of the vehicle symptoms/problems
            vehicle_info: Optional vehicle information for context
            
        Returns:
            Diagnostic advice and recommendations
        """
        context = ""
        if vehicle_info:
            context = f"""
Vehicle Details:
Make: {vehicle_info.get('make', 'Unknown')}
Model: {vehicle_info.get('model', 'Unknown')}
Year: {vehicle_info.get('year', 'Unknown')}
Mileage: {vehicle_info.get('mileage', 'Unknown')}
"""
        
        message = f"""I'm experiencing the following issue with my vehicle:

{symptoms}
{context}

Please help me diagnose the problem and suggest next steps."""
        
        return await self.chat(message)
    
    async def get_fuel_efficiency_tips(self, driving_habits: Dict[str, Any]) -> str:
        """
        Get personalized fuel efficiency tips based on driving habits.
        
        Args:
            driving_habits: Dictionary containing driving information
            
        Returns:
            Fuel efficiency recommendations
        """
        message = f"""Please provide fuel efficiency tips based on my driving habits:
        
Daily Commute Distance: {driving_habits.get('commute_distance', 'Unknown')} miles
Driving Environment: {driving_habits.get('environment', 'Mixed')} (city/highway/mixed)
Current MPG: {driving_habits.get('current_mpg', 'Unknown')}
Driving Style: {driving_habits.get('style', 'Normal')} (aggressive/normal/conservative)

Please provide specific tips to improve my fuel efficiency."""
        
        return await self.chat(message)
    
    def set_vehicle_profile(self, vehicle_info: Dict[str, Any]):
        """Set or update the vehicle profile."""
        self.vehicle_profile.update(vehicle_info)
    
    def get_vehicle_profile(self) -> Dict[str, Any]:
        """Get the current vehicle profile."""
        return self.vehicle_profile
    
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