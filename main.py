import asyncio
import uvicorn
from src.api import app
from src.ai_project.agent import initialize_vector_stores

async def main():
    # Khởi tạo vector stores trước khi bắt đầu
    try:
        print("Đang khởi tạo dữ liệu, vui lòng chờ...")
        result = initialize_vector_stores()  # Không dùng await nếu là hàm sync
        print("Khởi tạo dữ liệu thành công!")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo dữ liệu: {str(e)}")
        exit(1)

    # Chạy FastAPI app với Uvicorn
    print("\n🚀 Starting Davas Chatbot API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    asyncio.run(main())