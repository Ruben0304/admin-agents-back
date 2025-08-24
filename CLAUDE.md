# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is an **Admin System for Virtual Assistants Management** designed to provide centralized, plug & play administration of AI assistants across multiple applications.

### Core Functionality
The system enables you to:
- **Manage Multiple Apps**: Create and manage different applications (e.g., "App1", "App2") each with their own virtual assistants
- **Configure Assistants Per App**: Each app can have multiple assistants (e.g., "Assistant 1", "Assistant 2") with independent configurations
- **Dynamic Model Selection**: Change LLM providers and models through an admin panel without code modifications:
  - Switch between providers (Gemini, Cohere, OpenAI, etc.)
  - Select specific models within each provider (e.g., gemini-2.5-pro, command-r, gpt-4)
- **System Prompt Management**: Customize system prompts for each assistant through the admin interface
- **API Key Management**: Configure API keys for different providers through the admin panel
- **Zero-Code Configuration**: All changes are made through the admin interface, requiring no code deployments

### Use Case Example
1. Create "App1" with "Customer Support Assistant" and "Sales Assistant"
2. Configure Customer Support to use Gemini with a helpful support prompt
3. Configure Sales Assistant to use Cohere with a persuasive sales prompt
4. Switch providers/models instantly through the admin panel as needed
5. Add API keys for new providers without touching code

This architecture provides maximum flexibility for managing AI assistants across different applications with complete configuration control.

## Project Architecture

This is a FastAPI backend application structured following a layered architecture pattern:

- **`main.py`** - FastAPI application entry point, includes routers and basic endpoints
- **`models/`** - Pydantic models for request/response schemas (e.g., LoginRequest, LoginResponse)
- **`routers/`** - FastAPI route handlers organized by functionality (auth router with `/auth` prefix)
- **`services/`** - Business logic layer (AuthService handles authentication logic)
- **`providers/`** - LLM provider implementations with factory pattern for multiple AI services
- **`assistants/`** - Pre-built AI assistant implementations with specialized functionality

The authentication system uses hardcoded credentials (admin/password123) and returns mock JWT tokens.

## LLM Providers Architecture

The project uses a factory pattern for LLM providers organized by company with **full async support**:

```
providers/
├── llm_provider.py          # Abstract base class for all providers (async)
├── llm_factory.py           # Factory for creating provider instances
├── google/                  # Google AI services
│   └── gemini_provider.py   # Gemini async implementation (uses asyncio.to_thread)
└── cohere/                  # Cohere AI services
    └── cohere_provider.py   # Cohere async implementation (uses AsyncClientV2)
```

### Key Features
- **Fully Async**: All providers implement async methods for non-blocking operations
- **System Prompts**: Support for system prompts to define AI assistant roles and behavior
- **Provider-Specific Implementation**: 
  - **Cohere**: Uses native `AsyncClientV2` for true async operations
  - **Gemini**: Uses `asyncio.to_thread()` to wrap sync operations asynchronously

### Usage Examples
```python
from providers import chat_with_llm, LLMFactory
import asyncio

async def main():
    # Chat with any provider (async)
    response = await chat_with_llm("gemini", "gemini-2.5-pro", "Hello", streaming=False)
    
    # Chat with system prompt
    response = await chat_with_llm(
        "cohere", 
        "command-r", 
        "What can you help me with?", 
        system_prompt="You are a helpful programming assistant specialized in Python.",
        streaming=True, 
        api_key="optional"
    )

    # List available providers (sync method)
    print(LLMFactory.get_available_providers())  # ["gemini", "cohere"]

    # Register new providers (sync method)
    LLMFactory.register_provider("openai", OpenAIProvider)

asyncio.run(main())
```

### System Prompt Support
All providers now support system prompts to define the AI assistant's role:

```python
# Example with system prompt
response = await chat_with_llm(
    provider_name="gemini",
    model="gemini-2.5-pro", 
    prompt="How do I optimize this code?",
    system_prompt="You are an expert software engineer specializing in performance optimization.",
    streaming=False
)
```

## Assistants Architecture

The project includes pre-built AI assistants with specialized functionality organized in a modular structure:

```
assistants/
├── __init__.py                           # Exports for easy importing
├── base_assistant.py                     # Abstract base class for all assistants
├── MoneyTracker/                         # Personal finance assistant
│   ├── moneytracker.py                   # Core MoneyTracker assistant class
│   └── moneytracker_chatbot_service.py  # Service with specialized finance features
└── Suncar/                              # Automotive assistant
    ├── suncar.py                         # Core Suncar assistant class
    └── suncar_chatbot_service.py         # Service with specialized automotive features
```

### Base Assistant Class

All assistants inherit from `BaseAssistant` which provides:
- **LLM Integration**: Seamless integration with the LLM providers
- **System Prompt Management**: Default and custom system prompts
- **Async Chat**: Non-blocking conversation capabilities
- **Provider Flexibility**: Works with any registered LLM provider

### Available Assistants

#### MoneyTracker
Personal finance management assistant specializing in:
- Budget planning and expense tracking
- Financial goal setting and monitoring
- Investment advice for beginners
- Saving strategies and debt management
- Financial education and literacy

**Specialized Features**:
- `get_budget_advice()` - Personalized budget analysis
- `get_saving_plan()` - Goal-based saving strategies
- Conversation history tracking
- Financial calculations and recommendations

#### Suncar
Automotive services assistant specializing in:
- Vehicle maintenance schedules and reminders
- Car troubleshooting and diagnostic advice
- Automotive repair guidance
- Vehicle purchasing recommendations
- Fuel efficiency tips and driving advice

**Specialized Features**:
- `get_maintenance_schedule()` - Vehicle-specific maintenance plans
- `diagnose_problem()` - Symptom-based diagnostics
- `get_fuel_efficiency_tips()` - Personalized efficiency advice
- Vehicle profile management

### Usage Examples

```python
from assistants import MoneyTrackerChatbotService, SuncarChatbotService
import asyncio

async def main():
    # Initialize MoneyTracker with Gemini
    money_tracker = MoneyTrackerChatbotService(
        llm_provider="gemini",
        model="gemini-2.5-pro",
        api_key="your-api-key"
    )
    
    # Get budget advice
    response = await money_tracker.get_budget_advice(
        income=5000,
        expenses={"rent": 1500, "food": 600, "utilities": 200}
    )
    
    # Initialize Suncar with Cohere
    suncar = SuncarChatbotService(
        llm_provider="cohere",
        model="command-r",
        api_key="your-api-key"
    )
    
    # Get maintenance schedule
    response = await suncar.get_maintenance_schedule({
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "mileage": 45000
    })
    
    # Regular chat with custom prompt
    response = await money_tracker.chat(
        "What's the best way to save for retirement?",
        system_prompt="You are a conservative financial advisor focused on long-term stability."
    )

asyncio.run(main())
```

### Creating New Assistants

To create a new assistant:

1. **Create assistant folder**: `assistants/NewAssistant/`
2. **Implement core class**: Inherit from `BaseAssistant`
3. **Create service class**: Add specialized methods and features
4. **Define system prompt**: Specify the assistant's expertise and personality
5. **Update exports**: Add to `assistants/__init__.py`

Example structure:
```python
class NewAssistant(BaseAssistant):
    def __init__(self, llm_provider: str, model: str, api_key: Optional[str] = None):
        default_prompt = "You are a specialist in..."
        super().__init__(
            name="NewAssistant",
            llm_provider=llm_provider,
            model=model,
            default_system_prompt=default_prompt,
            api_key=api_key
        )
```

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI development server
uvicorn main:app --reload

# Run on specific port
uvicorn main:app --reload --port 8000
```

### Testing
Use `test_main.http` file for HTTP endpoint testing. It contains:
- Root endpoint test (`/`)
- Hello endpoint test (`/hello/{name}`)
- Auth login tests with valid/invalid credentials

### Environment Setup
Set environment variables in `.env`:
- `GEMINI_API_KEY` - For Google Gemini AI
- `COHERE_API_KEY` - For Cohere AI (optional)

## Key Dependencies
- **FastAPI** - Web framework
- **Pydantic** - Data validation and serialization
- **google-genai** - Google Gemini AI integration
- **cohere** - Cohere AI integration (optional)