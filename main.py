from fastapi import FastAPI
from routers import auth, chat, admin, assistants
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Admin Agents Backend",
    description="Backend API for managing AI assistants across multiple applications",
    version="1.0.0"
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
