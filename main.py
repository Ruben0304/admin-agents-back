from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import auth, chat, admin, assistants
from dotenv import load_dotenv
from providers.llm_factory import LLMFactory
from database.database import get_db
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load dynamic providers from database on startup"""
    try:
        # Load dynamic providers from database
        db = next(get_db())
        LLMFactory.load_dynamic_providers_from_db(db)
        print("✅ Dynamic providers loaded successfully from database")
    except Exception as e:
        print(f"⚠️ Warning: Could not load dynamic providers: {e}")
    
    yield
    
    # Cleanup on shutdown (if needed)
    print("🔄 Application shutting down")

app = FastAPI(
    title="Admin Agents Backend",
    description="Backend API for managing AI assistants across multiple applications",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide detailed error messages"""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"]
        })
    
    print(f"Validation error for {request.method} {request.url.path}:")
    for error in errors:
        print(f"  - {error['field']}: {error['message']} (type: {error['type']})")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation failed",
            "errors": errors
        }
    )

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(admin.router)

# Include assistant-specific routers
app.include_router(assistants.suncar_router)
app.include_router(assistants.moneytracker_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
