from fastapi import FastAPI
from .router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Davas Chatbot API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc một danh sách các URL bạn muốn cho phép
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả phương thức HTTP
    allow_headers=["*"],  # Cho phép tất cả headers
)

app.include_router(router, prefix="/api", tags=["chatbot"])

@app.get("/", tags=["health"])
def read_root():
    return {"message": "Welcome to Davas Chatbot API"}
