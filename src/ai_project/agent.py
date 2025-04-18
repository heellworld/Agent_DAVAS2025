import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import nest_asyncio
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from config.models_llm import llm_qwen25_3b
from .index_to_vectostore import load_data_vectostore, load_indexs


# Thiết lập cơ bản
load_dotenv()
nest_asyncio.apply()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Prompt template cải tiến với kỹ thuật Prompt Engineering
TEXT_CORRECTION_PROMPT = """
Bạn là chuyên viên hỗ trợ khách hàng tại sự kiện Danang Venture and Angel Summit. 
Hãy xử lý câu hỏi theo quy trình sau:

1. Xác định năm sự kiện liên quan trong câu hỏi (2024 hoặc 2025) (mặc định là năm 2025 nếu không đề cập)
2. Sử dụng công cụ truy vấn tương ứng (Davas2024/Davas2025)
3. Cung cấp thông tin chính xác, ngắn gọn từ tài liệu sự kiện
4. Nếu câu hỏi liên quan cả hai năm, so sánh thông tin từ cả hai nguồn

**CÂU HỎI:**  
"{text}"

Hãy trả lời bằng tiếng Việt, sử dụng thông tin từ các tài liệu được cung cấp.
"""
# Danh sách các sự kiện cần xử lý
report = ["Davas2024", "Davas2025"]

def initialize_vector_stores():
    # """Khởi tạo vector store cho các năm sự kiện"""
    load_data_vectostore("Davas2024", r"D:\project_company\Davas\src\data\Davas2024")
    load_data_vectostore("Davas2025", r"D:\project_company\Davas\src\data\Davas2025")

# Tạo query engines (cải tiến logging)
def create_query_engines():
    """Tạo công cụ truy vấn cho từng năm sự kiện"""
    query_engine_tools = []
    for symbol in report:
        try:
            index = load_indexs(symbol)
            query_engine = index.as_query_engine(
                similarity_top_k=5,
                llm=llm_qwen25_3b,
                response_mode="compact"
            )
            tool = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name=symbol,
                description=f"Dữ liệu chi tiết về sự kiện DAVAS {symbol[-4:]}"
            )
            query_engine_tools.append(tool)
        except Exception as e:
            logger.warning(f"Không tải được công cụ {symbol}: {str(e)}")
            continue
    return query_engine_tools

# Hàm chính của chatbot (thêm xử lý lỗi)
async def chatbot_agent(text: str):
    """Xử lý câu hỏi người dùng với cơ chế fallback"""
    try:
        query_engine_tools = create_query_engines()
        if not query_engine_tools:
            return "Xin lỗi, hệ thống đang cập nhật dữ liệu. Vui lòng thử lại sau."
        
        agent = ReActAgent.from_tools(
            tools=query_engine_tools,
            llm=llm_qwen25_3b,
            verbose=True
        )
        
        formatted_prompt = TEXT_CORRECTION_PROMPT.format(text=text)
        response = agent.chat(formatted_prompt)
        return str(response) if response else "Không tìm thấy thông tin liên quan"
    
    except Exception as e:
        logger.error(f"Lỗi xử lý câu hỏi: {str(e)}", exc_info=True)
        return "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
    