from fastapi import APIRouter, HTTPException
from ..ai_project.agent import chatbot_agent
from .models import ChatRequest, ChatResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received query: {request.query}")
        response_text = await chatbot_agent(request.query) # Gọi hàm chatbot_agent bất đồng bộ
        logger.info(f"Sending response: {response_text}")
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Lỗi xử lý yêu cầu chat.") 