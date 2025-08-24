from fastapi import FastAPI
from routers import auth, chat
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
