from fastapi import FastAPI
from .router import router

app = FastAPI(title="Davas Chatbot API")

app.include_router(router, prefix="/api", tags=["chatbot"])

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Welcome to Davas Chatbot API"}
