from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database.database import get_db
from repositories import *
from models.chat import AssistantChatRequest, AssistantChatResponse
from providers import chat_with_llm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import AuthService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/moneytracker", tags=["MoneyTracker Assistant"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    token = credentials.credentials
    user_data = AuthService.verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_data

@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_moneytracker(
    request: AssistantChatRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Chat with MoneyTracker financial assistant.
    This endpoint loads MoneyTracker's configuration from the database.
    """
    try:
        # Get MoneyTracker assistant from database by name
        assistant = crud.get_assistant_by_name(db, "MoneyTracker")
        if not assistant:
            raise HTTPException(status_code=404, detail="MoneyTracker assistant not found")
        
        if not assistant.is_active:
            raise HTTPException(status_code=400, detail="MoneyTracker assistant is not active")
        
        # Get the model and provider information
        model = assistant.model
        provider = model.provider
        
        # Get API key (from assistant or provider's api_keys)
        api_key = assistant.api_key
        if not api_key:
            # Get provider's default API key
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                # Use first active API key (in real app, decrypt it)
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Chat with LLM using MoneyTracker's configuration from database
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=request.message,
            system_prompt=assistant.system_prompt,
            streaming=assistant.is_streaming,
            api_key=api_key
        )
        
        return AssistantChatResponse(
            response=response,
            assistant_name=assistant.name,
            provider=provider.display_name,
            model=model.display_name,
            streaming_used=assistant.is_streaming
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_moneytracker_info(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get MoneyTracker assistant information and configuration"""
    try:
        assistant = crud.get_assistant_by_name(db, "MoneyTracker")
        if not assistant:
            raise HTTPException(status_code=404, detail="MoneyTracker assistant not found")
        
        return {
            "assistant_name": assistant.name,
            "description": assistant.description,
            "system_prompt": assistant.system_prompt,
            "model": assistant.model.display_name,
            "provider": assistant.model.provider.display_name,
            "streaming_enabled": assistant.is_streaming,
            "is_active": assistant.is_active,
            "created_at": assistant.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/budget-advice")
async def get_budget_advice(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get personalized budget advice using MoneyTracker's financial expertise.
    This is a specialized endpoint for budget planning.
    """
    try:
        # Get MoneyTracker assistant
        assistant = crud.get_assistant_by_name(db, "MoneyTracker")
        if not assistant:
            raise HTTPException(status_code=404, detail="MoneyTracker assistant not found")
        
        # Create specialized prompt for budget advice
        budget_prompt = f"""
        As a specialized financial planning assistant, provide comprehensive budget advice for:
        
        Monthly Income: ${request.get('monthly_income', 0)}
        Monthly Expenses: ${request.get('monthly_expenses', 0)}
        Financial Goals: {request.get('financial_goals', 'No specific goals')}
        Current Savings: ${request.get('current_savings', 0)}
        Debt Amount: ${request.get('debt_amount', 0)}
        Age: {request.get('age', 'Unknown')}
        
        Please provide:
        1. Budget breakdown (50/30/20 rule or custom)
        2. Expense reduction strategies
        3. Savings recommendations
        4. Debt payoff strategies
        5. Emergency fund advice
        6. Investment suggestions (if applicable)
        """
        
        # Get model and provider info
        model = assistant.model
        provider = model.provider
        
        # Get API key
        api_key = assistant.api_key
        if not api_key:
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Get budget advice from LLM
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=budget_prompt,
            system_prompt=assistant.system_prompt,
            streaming=False,
            api_key=api_key
        )
        
        return {
            "budget_advice": response,
            "financial_profile": request,
            "generated_at": datetime.now().isoformat(),
            "assistant": "MoneyTracker"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/saving-plan")
async def create_saving_plan(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a personalized saving plan using MoneyTracker's financial expertise.
    This is a specialized endpoint for saving strategies.
    """
    try:
        # Get MoneyTracker assistant
        assistant = crud.get_assistant_by_name(db, "MoneyTracker")
        if not assistant:
            raise HTTPException(status_code=404, detail="MoneyTracker assistant not found")
        
        # Create specialized prompt for saving plan
        saving_prompt = f"""
        As a specialized financial planning assistant, create a detailed saving plan for:
        
        Goal: {request.get('saving_goal', 'General savings')}
        Target Amount: ${request.get('target_amount', 0)}
        Timeframe: {request.get('timeframe_months', 12)} months
        Monthly Income: ${request.get('monthly_income', 0)}
        Current Monthly Savings: ${request.get('current_monthly_savings', 0)}
        Risk Tolerance: {request.get('risk_tolerance', 'Moderate')}
        
        Please provide:
        1. Monthly savings target
        2. Savings strategies and tips
        3. Timeline breakdown
        4. Potential obstacles and solutions
        5. Investment options (if applicable)
        6. Progress tracking methods
        """
        
        # Get model and provider info
        model = assistant.model
        provider = model.provider
        
        # Get API key
        api_key = assistant.api_key
        if not api_key:
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Get saving plan from LLM
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=saving_prompt,
            system_prompt=assistant.system_prompt,
            streaming=False,
            api_key=api_key
        )
        
        return {
            "saving_plan": response,
            "goal_info": request,
            "created_at": datetime.now().isoformat(),
            "assistant": "MoneyTracker"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/investment-advice")
async def get_investment_advice(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get investment advice using MoneyTracker's financial expertise.
    This is a specialized endpoint for investment guidance.
    """
    try:
        # Get MoneyTracker assistant
        assistant = crud.get_assistant_by_name(db, "MoneyTracker")
        if not assistant:
            raise HTTPException(status_code=404, detail="MoneyTracker assistant not found")
        
        # Create specialized prompt for investment advice
        investment_prompt = f"""
        As a specialized financial investment advisor, provide investment guidance for:
        
        Investment Goal: {request.get('investment_goal', 'Long-term growth')}
        Investment Amount: ${request.get('investment_amount', 0)}
        Time Horizon: {request.get('time_horizon', '5-10 years')}
        Risk Tolerance: {request.get('risk_tolerance', 'Moderate')}
        Current Portfolio: {request.get('current_portfolio', 'No existing investments')}
        Age: {request.get('age', 'Unknown')}
        
        Please provide:
        1. Asset allocation recommendations
        2. Investment vehicle suggestions
        3. Risk management strategies
        4. Expected returns and volatility
        5. Rebalancing frequency
        6. Tax considerations
        """
        
        # Get model and provider info
        model = assistant.model
        provider = model.provider
        
        # Get API key
        api_key = assistant.api_key
        if not api_key:
            api_keys = crud.get_api_keys_by_provider(db, provider.id)
            if api_keys:
                api_key = api_keys[0].encrypted_key.replace("encrypted_", "")
        
        # Get investment advice from LLM
        response = await chat_with_llm(
            provider_name=provider.name,
            model=model.name,
            prompt=investment_prompt,
            system_prompt=assistant.system_prompt,
            streaming=False,
            api_key=api_key
        )
        
        return {
            "investment_advice": response,
            "investment_profile": request,
            "generated_at": datetime.now().isoformat(),
            "assistant": "MoneyTracker"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 