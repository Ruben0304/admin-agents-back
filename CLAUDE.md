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
- **Dynamic Provider Creation**: Create custom LLM providers with Python code through admin interface:
  - Code templates for popular providers (OpenAI, Anthropic, etc.)
  - Real-time validation and testing framework
  - Secure code execution environment
  - Template-based provider setup with configuration schemas
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

## Recent Updates & Current Status

### Latest Refactoring (2024)

- **Streamlined Router Architecture**: Simplified router inclusion in `main.py` with direct imports
- **Enhanced Database Integration**: All assistant operations now use direct repository function calls
- **Improved Testing Suite**: Added comprehensive HTTP test files covering all major functionality
- **Modular Repository Pattern**: Implemented clean separation of database operations across entities
- **Enhanced Authentication**: Strengthened JWT-based auth with proper role-based access control
- **Simplified Admin Endpoints**: Refactored admin CRUD endpoints to be direct and simple, removing recursion issues
- **Endpoint Field Integration**: Added endpoint field support for applications and assistants stored in database

### Current Implementation Status

✅ **Completed Features:**
- Full PostgreSQL database integration with SQLAlchemy ORM
- JWT authentication with role-based access control
- Simplified admin CRUD endpoints for all entities (applications, providers, models, assistants, users, API keys)
- **Dynamic Provider System**: Complete implementation with database storage and code execution
- **Provider Templates**: Pre-built code templates for OpenAI, Anthropic, and other popular providers
- **Code Validation & Testing**: Real-time Python code validation and live API testing framework
- **Route Ordering Fix**: Proper FastAPI route precedence for dynamic vs static provider endpoints
- Endpoint field support for applications and assistants with database storage
- Direct database query operations without complex repository abstractions
- Complete error-free admin API with proper response models
- LLM provider factory with async support (Gemini, Cohere, Dynamic Providers)
- Database-first assistant configuration loading
- Complete HTTP test suite for all endpoints

🚧 **In Progress:**
- Additional LLM provider integrations (OpenAI, Claude, etc.)
- Advanced assistant features and specialized endpoints
- Frontend admin panel development
- Enhanced monitoring and logging capabilities

## Project Architecture

This is a FastAPI backend application structured following a layered architecture pattern with **PostgreSQL database integration**:

- **`main.py`** - FastAPI application entry point with direct router inclusion:
  ```python
  # Core routers
  app.include_router(auth.router)
  app.include_router(chat.router)
  app.include_router(admin.router)
  
  # Assistant-specific routers
  app.include_router(assistants.suncar_router)
  app.include_router(assistants.moneytracker_router)
  ```
- **`models/`** - Pydantic models for request/response schemas and database operations
- **`routers/`** - FastAPI route handlers organized by functionality:
  - `/auth` - Authentication endpoints with JWT token management
  - `/admin` - Comprehensive admin panel for managing all system entities
  - `/chat` - Chat endpoints for assistant interactions (database-backed)
  - **`assistants/`** - Specialized routers for dedicated assistant endpoints:
    - `/suncar/` - Suncar automotive assistant with specialized endpoints
    - `/moneytracker/` - MoneyTracker financial assistant with specialized endpoints
- **`services/`** - Business logic layer with database-backed authentication
- **`providers/`** - LLM provider implementations with factory pattern for multiple AI services
- **`assistants/`** - Pre-built AI assistant implementations with specialized functionality
- **`repositories/`** - Modular database operations layer:
  - `user_repository.py` - User CRUD operations
  - `application_repository.py` - Application CRUD operations
  - `provider_repository.py` - Provider CRUD operations
  - `model_repository.py` - Model CRUD operations
  - `assistant_repository.py` - Assistant CRUD operations
  - `api_key_repository.py` - API Key CRUD operations
- **`database/`** - PostgreSQL database layer:
  - `models.py` - SQLAlchemy database models
  - `database.py` - Database connection and session management

## Database Architecture

The system uses PostgreSQL with the following main tables:

### Repository Layer Architecture

The system implements a **modular repository pattern** for clean separation of database operations:

```
repositories/
├── __init__.py                    # Exports all repository functions
├── user_repository.py             # User CRUD operations
├── application_repository.py      # Application CRUD operations
├── provider_repository.py         # Provider CRUD operations
├── model_repository.py            # Model CRUD operations
├── assistant_repository.py        # Assistant CRUD operations
└── api_key_repository.py          # API Key CRUD operations
```

**Benefits of Repository Pattern**:

- **Separation of Concerns**: Each entity has its own repository file
- **Maintainability**: Easy to locate and modify specific database operations
- **Testability**: Individual repositories can be tested in isolation
- **Scalability**: New repositories can be added without affecting existing ones
- **Clean Imports**: Single import statement provides access to all operations

**Usage**:

```python
from repositories import *

# All repository functions are available
user = get_user_by_username(db, "admin")
assistant = get_assistant_by_name(db, "Suncar")
applications = get_applications(db)
```

### Core Tables

- **`users`** - User accounts with bcrypt password hashing, role-based access control
  - Fields: `id`, `username`, `email`, `hashed_password`, `full_name`, `is_active`, `is_admin`
  - Timestamps: `created_at`, `updated_at`

- **`applications`** - Applications that contain assistants (e.g., "E-Commerce App")
  - Fields: `id`, `name`, `description`, `icon_url`, `endpoint`, `is_active`, `created_by`
  - Special Fields: `endpoint` (String) - Custom API endpoint for this application
  - Relationships: One-to-many with assistants
  - Timestamps: `created_at`, `updated_at`

- **`providers`** - LLM providers (Gemini, Cohere, OpenAI) with display names and icons, supports dynamic providers
  - Fields: `id`, `name`, `display_name`, `icon_url`, `base_url`, `is_active`
  - **Dynamic Provider Fields**:
    - `is_dynamic` (Boolean) - Distinguishes user-created vs built-in providers
    - `python_code` (Text) - Custom Python implementation code
    - `required_dependencies` (JSON) - List of pip packages needed
    - `config_schema` (JSON) - Schema for API keys and configuration variables
    - `validation_code` (Text) - Code to test provider API connectivity
  - Relationships: One-to-many with models
  - Timestamps: `created_at`, `updated_at`

- **`models`** - Specific models per provider (e.g., "gemini-2.5-pro", "gpt-4o")
  - Fields: `id`, `name`, `display_name`, `provider_id`, `max_tokens`, `supports_streaming`, `supports_system_prompt`, `cost_per_token`, `is_active`
  - Relationships: Many-to-one with provider, one-to-many with assistants
  - Timestamps: `created_at`, `updated_at`

- **`assistants`** - AI assistants with configurable system prompts and streaming settings
  - Fields: `id`, `name`, `description`, `system_prompt`, `application_id`, `model_id`, `api_key`, `is_streaming`, `is_active`, `config` (JSON), `endpoint`, `created_by`
  - Special Fields: `endpoint` (String) - Custom API endpoint for this assistant
  - Relationships: Many-to-one with application and model
  - Timestamps: `created_at`, `updated_at`

- **`api_keys`** - Encrypted API key storage per provider
  - Fields: `id`, `name`, `provider_id`, `encrypted_key`, `is_active`, `created_by`
  - Relationships: Many-to-one with provider
  - Timestamps: `created_at`, `updated_at`

### Authentication System

The system uses **database-backed JWT authentication** with:

- Secure password hashing using bcrypt
- JWT tokens with expiration (30 minutes default)
- Role-based access control (admin/regular users)
- **Default credentials**: `admin / password123` and `user1 / user123`

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

### Database-First Architecture

**IMPORTANT**: All assistants now load their configuration (system prompt, streaming settings, provider, model, API keys) from the PostgreSQL database. Only the user's message prompt is provided dynamically.

### Base Assistant Class

All assistants inherit from `BaseAssistant` which provides:

- **Database Integration**: Load all configuration from PostgreSQL database
- **LLM Integration**: Seamless integration with the LLM providers
- **System Prompt Management**: System prompts loaded from database
- **Async Chat**: Non-blocking conversation capabilities
- **Provider Flexibility**: Works with any registered LLM provider
- **Dual Initialization**: Support for both database loading and manual configuration

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

#### Option 1: Load Assistant from Database (Recommended)

```python
from assistants import MoneyTracker, Suncar, BaseAssistant
from database.database import get_db
import asyncio

async def main():
    db = next(get_db())

    # Load MoneyTracker assistant from database by ID
    # This gets ALL configuration from DB: system prompt, provider, model, streaming, API key
    money_tracker = MoneyTracker(assistant_id=1, db=db)

    # Chat using database configuration
    response = await money_tracker.chat("What's the best way to save for retirement?")

    # Load Suncar assistant from database
    suncar = Suncar(assistant_id=2, db=db)

    # Chat with database-configured assistant
    response = await suncar.chat("When should I change my oil?")

    # Alternative: Use BaseAssistant directly
    assistant = BaseAssistant.from_database(assistant_id=1, db=db)
    response = await assistant.chat("Hello!")

asyncio.run(main())
```

#### Option 2: Manual Configuration (Legacy Support)

```python
from assistants import MoneyTracker, Suncar
import asyncio

async def main():
    # Still supported for backwards compatibility
    money_tracker = MoneyTracker(
        llm_provider="gemini",
        model="gemini-2.5-pro",
        api_key="your-api-key",
        streaming=False
    )

    response = await money_tracker.chat("Help me with budgeting")

    suncar = Suncar(
        llm_provider="cohere",
        model="command-r",
        api_key="your-api-key",
        streaming=True
    )

    response = await suncar.chat("Car maintenance tips?")

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

#### Available Test Files

The project includes several HTTP test files for comprehensive API testing:

- **`test_main.http`** - Basic endpoint testing:
  - Root endpoint test (`/`)
  - Hello endpoint test (`/hello/{name}`)

- **`test_auth_flow.http`** - Authentication flow testing:
  - User login with valid/invalid credentials
  - JWT token validation
  - Protected endpoint access

- **`test_admin.http`** - Admin panel endpoints testing:
  - Application management (CRUD operations)
  - Provider and model management
  - Assistant configuration
  - API key management
  - User management (admin operations)

- **`test_assistants.http`** - General assistant functionality testing:
  - Database-backed assistant chat
  - Provider-specific testing
  - Configuration loading from database

#### Assistant Routers Testing

Use **`test_assistants_routers.http`** file for testing the specialized assistant-specific routers:

**Suncar Assistant Endpoints**:

- `GET /suncar/info` - Get assistant information
- `POST /suncar/chat` - General chat functionality
- `POST /suncar/maintenance-schedule` - Vehicle maintenance scheduling
- `POST /suncar/diagnose-problem` - Vehicle problem diagnosis

**MoneyTracker Assistant Endpoints**:

- `GET /moneytracker/info` - Get assistant information
- `POST /moneytracker/chat` - General chat functionality
- `POST /moneytracker/budget-advice` - Budget planning advice
- `POST /moneytracker/saving-plan` - Saving plan creation
- `POST /moneytracker/investment-advice` - Investment guidance

**Testing Setup**:

1. Set `@base_url` to your server URL (default: `http://localhost:8000`)
2. Set `@auth_token` to a valid JWT token from `/auth/login`
3. Run individual requests to test specific endpoints

### Environment Setup

Configure your `.env` file with:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/admin_agents

# Authentication
SECRET_KEY=your-secret-key-change-this-in-production

# API Keys for LLM Providers
GEMINI_API_KEY=your-gemini-api-key-here
COHERE_API_KEY=your-cohere-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

## Admin API Endpoints

The system provides **simple and direct CRUD endpoints** for managing all entities with **endpoint field support**:

### Authentication

- `POST /auth/login` - User authentication with JWT tokens

### Applications CRUD

- `GET /admin/applications` - List all applications (includes `endpoint` field from database)
- `POST /admin/applications` - Create new application (admin only, supports `endpoint` field)
- `GET /admin/applications/{id}` - Get specific application (includes `endpoint` field)

**Example Response**:
```json
{
  "id": 1,
  "name": "E-Commerce App",
  "description": "Customer support application",
  "icon_url": "https://example.com/icon.png",
  "endpoint": "/api/v1/ecommerce",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

### Providers & Models CRUD

- `GET /admin/providers` - List all LLM providers (static and dynamic)
- `GET /admin/providers/{provider_id}` - Get specific provider
- `GET /admin/providers/{provider_id}/models` - Get models for specific provider
- `GET /admin/models` - Get all models across all providers
- `GET /admin/models/{model_id}` - Get specific model
- `POST /admin/models` - Create new model (admin only)

### Dynamic Provider Management (Admin only)

**IMPORTANT**: Dynamic provider routes must come before generic provider routes in FastAPI to avoid path conflicts.

- `GET /admin/providers/dynamic` - List all user-created dynamic providers
- `POST /admin/providers/dynamic` - Create new dynamic provider with custom Python code
- `GET /admin/providers/dynamic/{id}` - Get specific dynamic provider details
- `PUT /admin/providers/dynamic/{id}` - Update dynamic provider code and configuration
- `DELETE /admin/providers/dynamic/{id}` - Soft delete dynamic provider
- `GET /admin/providers/dynamic/{id}/code` - Get provider Python code (admin only for security)
- `POST /admin/providers/dynamic/test` - Test provider code with real API calls before deployment
- `POST /admin/providers/code/validate` - Validate Python code syntax and structure
- `GET /admin/providers/code/template?provider_type=openai` - Get code templates for different providers
- `POST /admin/providers/dynamic/debug` - Debug endpoint for troubleshooting provider creation

**Example Dynamic Provider Response**:
```json
{
  "id": 1,
  "name": "custom_openai",
  "display_name": "Custom OpenAI Provider",
  "icon_url": "https://example.com/openai.png",
  "base_url": "https://api.openai.com/v1",
  "is_active": true,
  "is_dynamic": true,
  "config_schema": {
    "api_key": {"type": "string", "required": true},
    "max_tokens": {"type": "integer", "default": 1000}
  },
  "required_dependencies": ["openai", "requests"],
  "has_validation_code": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### Assistants CRUD

- `GET /admin/assistants` - Get all assistants across all applications (includes `endpoint` field)
- `GET /admin/applications/{app_id}/assistants` - Get assistants for specific application
- `GET /admin/assistants/{assistant_id}` - Get specific assistant (includes `endpoint` field)
- `POST /admin/assistants` - Create new assistant (supports `endpoint` field)
- `PUT /admin/assistants/{assistant_id}` - Update assistant configuration (supports `endpoint` field)

**Example Response**:
```json
{
  "id": 1,
  "name": "Customer Support Bot",
  "description": "Helps with customer inquiries",
  "system_prompt": "You are a helpful customer support assistant...",
  "application_id": 1,
  "model_id": 1,
  "endpoint": "/chat/customer-support",
  "is_streaming": true,
  "is_active": true,
  "config": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

### User Management

- `POST /admin/users` - Create new user (admin only)

### API Keys CRUD

- `GET /admin/providers/{provider_id}/api-keys` - Get API keys for provider (admin only)
- `POST /admin/api-keys` - Store encrypted API key (admin only)

### Chat Endpoints

- `POST /chat/` - Direct chat with specified provider, model, and configuration
- `POST /chat/assistant` - **Chat with assistant using database configuration** (loads all settings from DB)
- `GET /chat/test` - Test endpoint for Gemini provider

### Key Features

- **Simple Direct Queries**: All endpoints use direct database queries without complex abstractions
- **Endpoint Field Support**: Applications and assistants include `endpoint` field stored in database
- **Error-Free Operation**: Resolved all recursion and TypeError issues
- **Proper Response Models**: All endpoints return structured JSON with correct field mapping
- **JWT Authentication**: All endpoints require valid authentication tokens
- **Admin-Only Operations**: Sensitive operations require admin privileges

## Application-Specific Router Architecture

The system implements **dedicated routers for specific assistants** that provide specialized endpoints for each AI assistant. This architecture offers clean, organized API access with domain-specific functionality for each assistant type.

### Implemented Assistant Routers

#### Suncar Automotive Assistant Router (`/suncar/`)

**Location**: `routers/assistants/suncar_router.py`

**Endpoints**:

- `POST /suncar/chat` - General chat with Suncar automotive assistant
- `GET /suncar/info` - Get Suncar assistant configuration and information
- `POST /suncar/maintenance-schedule` - Get personalized vehicle maintenance schedule
- `POST /suncar/diagnose-problem` - Diagnose vehicle problems with specialized prompts

**Specialized Features**:

- Vehicle maintenance scheduling with make, model, year, and mileage
- Problem diagnosis with symptoms and vehicle context
- Automotive expertise through specialized system prompts
- Database-driven configuration loading

#### MoneyTracker Financial Assistant Router (`/moneytracker/`)

**Location**: `routers/assistants/moneytracker_router.py`

**Endpoints**:

- `POST /moneytracker/chat` - General chat with MoneyTracker financial assistant
- `GET /moneytracker/info` - Get MoneyTracker assistant configuration and information
- `POST /moneytracker/budget-advice` - Get personalized budget planning advice
- `POST /moneytracker/saving-plan` - Create customized saving plans
- `POST /moneytracker/investment-advice` - Get investment guidance and strategies

**Specialized Features**:

- Budget analysis with income, expenses, and financial goals
- Saving plan creation with timeframe and risk tolerance
- Investment advice with portfolio context and time horizon
- Financial expertise through specialized system prompts
- Database-driven configuration loading

### Router Architecture Benefits

1. **Domain Separation**: Each assistant has its own router with specialized endpoints
2. **Clean URLs**: Intuitive endpoint structure (`/suncar/maintenance-schedule`)
3. **Specialized Functionality**: Endpoints tailored to each assistant's expertise
4. **Database Integration**: All configuration loaded from PostgreSQL database
5. **Authentication**: JWT-based security for all endpoints
6. **Modular Design**: Easy to add new assistants and endpoints

### Usage Examples

```bash
# Suncar Automotive Assistant
POST /suncar/maintenance-schedule
{
    "vehicle_make": "Toyota",
    "vehicle_model": "Corolla",
    "year": 2020,
    "current_mileage": 45000
}

# MoneyTracker Financial Assistant
POST /moneytracker/budget-advice
{
    "monthly_income": 3000,
    "monthly_expenses": 2200,
    "financial_goals": "Save for vacation",
    "current_savings": 1500,
    "debt_amount": 5000,
    "age": 28
}
```

### Adding New Assistant Routers

To create a new assistant router:

1. **Create router file**: `routers/assistants/new_assistant_router.py`
2. **Implement endpoints**: Add specialized functionality for the assistant
3. **Update main.py**: Include the new router
4. **Update **init**.py**: Export the router

Example structure:

```python
router = APIRouter(prefix="/newassistant", tags=["NewAssistant"])

@router.post("/chat")
async def chat_with_assistant(request: AssistantChatRequest):
    # Implementation here
    pass

@router.post("/specialized-feature")
async def specialized_feature(request: dict):
    # Specialized functionality here
    pass
```

## Legacy Application-Specific Router Architecture

The system previously implemented **dynamic application-specific routers** that create dedicated endpoints for each application and its assistants. This provides clean, organized API access for each application independently.

### Router Structure

For each application in the database, the system automatically generates:

- **Application Router**: Main router for the application (`/app/{app_name}/`)
- **Assistant Endpoints**: Individual chat endpoints for each assistant within the application

### URL Pattern Examples

```
/app/ecommerce/                          # Main application endpoint
/app/ecommerce/customer-support          # Customer Support Assistant chat
/app/ecommerce/sales-assistant           # Sales Assistant chat
/app/ecommerce/product-helper            # Product Helper Assistant chat

/app/banking/                            # Banking application
/app/banking/account-manager             # Account Manager Assistant chat
/app/banking/loan-advisor                # Loan Advisor Assistant chat
/app/banking/fraud-detection             # Fraud Detection Assistant chat
```

### Implementation Architecture

#### Router Factory Pattern

```python
# routers/app_factory.py
class ApplicationRouterFactory:
    @staticmethod
    def create_application_router(app_name: str, assistants: List[Assistant]) -> APIRouter:
        """Creates a dedicated router for an application with all its assistant endpoints"""

    @staticmethod
    def create_assistant_endpoint(assistant: Assistant) -> Callable:
        """Creates individual chat endpoint for a specific assistant"""
```

#### Dynamic Router Registration

```python
# main.py - Application startup
async def setup_application_routers():
    """Dynamically registers routers for all applications in the database"""
    db = next(get_db())
    applications = get_all_applications(db)

    for app in applications:
        # Create router for this application
        app_router = ApplicationRouterFactory.create_application_router(
            app_name=app.name,
            assistants=app.assistants
        )

        # Register router with FastAPI
        main_app.include_router(
            app_router,
            prefix=f"/app/{app.name.lower().replace(' ', '-')}",
            tags=[f"App: {app.name}"]
        )
```

### Assistant Chat Endpoints

Each assistant gets its own dedicated chat endpoint with the following structure:

#### Endpoint Format

```
POST /app/{app_name}/{assistant_name}
```

#### Request/Response Models

```python
# Chat with specific assistant
class AssistantChatRequest(BaseModel):
    message: str
    stream: Optional[bool] = None  # Override assistant's default streaming setting

class AssistantChatResponse(BaseModel):
    response: str
    assistant_name: str
    application: str
    timestamp: datetime
    provider_used: str
    model_used: str
```

#### Example API Calls

```bash
# Chat with Customer Support Assistant in E-Commerce app
POST /app/ecommerce/customer-support
{
    "message": "I need help with my order",
    "stream": false
}

# Chat with Account Manager in Banking app
POST /app/banking/account-manager
{
    "message": "What's my account balance?",
    "stream": true
}
```

### Authentication & Authorization

Application-specific routers maintain the same authentication requirements:

- **JWT Token Required**: All assistant chat endpoints require valid authentication
- **Application Access Control**: Users can be restricted to specific applications
- **Assistant-Level Permissions**: Fine-grained control over which assistants users can access

### Dynamic Router Updates

The system supports **hot-reloading** of application routers:

- **Database Changes**: When applications or assistants are added/modified through admin panel
- **Automatic Re-registration**: System detects changes and updates routes without restart
- **Zero Downtime**: New assistants become available immediately

### Benefits of This Architecture

1. **Clean API Organization**: Each application has its own namespace
2. **Intuitive URLs**: Easy to understand and remember endpoint patterns
3. **Scalable Structure**: Add new applications without code changes
4. **Independent Configuration**: Each assistant endpoint uses its own database configuration
5. **Automatic Documentation**: FastAPI automatically generates docs for all dynamic endpoints
6. **Version Control**: Applications can have different API versions if needed

### Usage in Client Applications

Client applications can easily integrate with their dedicated endpoints:

```javascript
// E-Commerce application client code
const chatWithSupport = async (message) => {
  const response = await fetch("/app/ecommerce/customer-support", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, stream: false }),
  });
  return response.json();
};

// Banking application client code
const chatWithAccountManager = async (message) => {
  const response = await fetch("/app/banking/account-manager", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, stream: true }),
  });
  return response.json();
};
```

## Key Dependencies

- **FastAPI** - Modern web framework with automatic API documentation and async support
- **SQLAlchemy** - Database ORM with PostgreSQL support and relationship management
- **Alembic** - Database migration tool for schema versioning
- **Pydantic** - Data validation and serialization with type hints
- **passlib[bcrypt]** - Secure password hashing with bcrypt algorithm
- **python-jose[cryptography]** - JWT token creation and validation
- **psycopg2-binary** - PostgreSQL database driver with binary packages
- **python-dotenv** - Environment variable loading from .env files
- **uvicorn** - ASGI server for running FastAPI applications
- **google-genai** - Google Gemini AI integration with async support
- **cohere** - Cohere AI integration with AsyncClientV2
