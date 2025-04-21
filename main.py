import uvicorn
from src.api import app
from src.ai_project.agent import initialize_vector_stores
import asyncio

if __name__ == "__main__":
    # # Khởi tạo vector stores trước khi bắt đầu
    # try:
    #     print("Đang khởi tạo dữ liệu, vui lòng chờ...")
    #     asyncio.run(initialize_vector_stores())
    #     print("Khởi tạo dữ liệu thành công!")
    # except Exception as e:
    #     print(f"❌ Lỗi khởi tạo dữ liệu: {str(e)}")
    #     exit(1)

    print("\n🚀 Starting Davas Chatbot API server...")
    # Chạy FastAPI app với Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) # reload=True để tự động load lại khi có thay đổi code

