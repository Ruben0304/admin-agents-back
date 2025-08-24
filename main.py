from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chat, admin, assistants
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Admin Agents Backend",
    description="Backend API for managing AI assistants across multiple applications",
    version="1.0.0"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
