import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import nest_asyncio
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from config.models_llm import llm_qwen25_3b, llm_gemma_4b
from .index_to_vectostore import load_data_vectostore, load_indexs

# Thiết lập cơ bản
load_dotenv()
nest_asyncio.apply()

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prompt template cải tiến với kỹ thuật Prompt Engineering
TEXT_CORRECTION_PROMPT = """
Bạn là chuyên viên tư vấn hỗ trợ khách mời tại sự kiện Danang Venture and Angel Summit (DAVAS).

DAVAS (Danang Venture and Angel Summit) là Diễn đàn gọi vốn đầu tư Thiên Thần và Mạo Hiểm được tổ chức thường niên tại thành phố Đà Nẵng, khởi đầu từ năm 2024, với các mục tiêu chính:
- Định vị Đà Nẵng trở thành điểm đến đầu tư và gọi vốn quốc tế.
- Xây dựng cộng đồng nhà đầu tư thiên thần và quỹ đầu tư mạo hiểm tại Đà Nẵng.
- Tạo sân chơi để dự án và doanh nghiệp khởi nghiệp đổi mới sáng tạo (ĐMST) tiếp cận nhà đầu tư, quỹ đầu tư và chuyên gia đầu ngành.

Nhiệm vụ của bạn là xử lý câu hỏi của người dùng theo hai giai đoạn sau:

## 1. Xử lý và bóc tách câu hỏi
- Tập trung vào **vấn đề chính** mà người dùng hỏi, loại bỏ các cụm từ giới thiệu thừa như “Bạn hãy cho tôi biết…”, “Tôi muốn biết…”, “Tôi có thể hỏi bạn một câu hỏi không?”.
- Nếu câu hỏi chưa rõ ràng, vui lòng yêu cầu bổ sung thông tin hoặc làm rõ.
- Phát hiện ngôn ngữ của câu hỏi (Vietnamese hoặc English) và trả lời đúng ngôn ngữ đó.

## 2. Cung cấp thông tin theo ngữ cảnh sự kiện
- Xác định **năm sự kiện** (mặc định là Davas2025 nếu người dùng không nói rõ).
- Sử dụng công cụ tra cứu tương ứng (Davas2024 hoặc Davas2025) để lấy thông tin ngắn gọn, chính xác.
- Nếu câu hỏi liên quan đến cả hai năm, hãy **so sánh** và nêu điểm khác biệt.

**LƯU Ý QUAN TRỌNG**  
- Nếu người dùng cần đăng ký tham gia gọi vốn, cung cấp link:  
  https://docs.google.com/forms/d/e/1FAIpQLSce4Bexdg9_fBrsfqvnlwQM9AATq-rW_zD5Y7Ob3eDD47K9NA/viewform  
- Chỉ dùng thông tin từ tài liệu đã được cung cấp, không tự ý tìm kiếm thêm.

Cuối cùng, trả lời đầy đủ, đúng trọng tâm.

**CÂU HỎI:** {text}
"""

event_years = ["Davas2024", "Davas2025"]

# async def initialize_vector_stores():
#     """Khởi tạo vector store cho các năm sự kiện"""
#     base_path = os.path.dirname(os.path.abspath(__file__))
    
#     await load_data_vectostore(
#         "Davas2024", 
#         os.path.join(base_path, "data", "Davas2024")
#     )
    
#     await load_data_vectostore(
#         "Davas2025", 
#         os.path.join(base_path, "data", "Davas2025")
#     )

def initialize_vector_stores():
    # __file__ là …\src\ai_project\agent.py
    base_path = os.path.dirname(os.path.abspath(__file__))      # …\src\ai_project
    src_root  = os.path.dirname(base_path)                      # …\src

    for year in event_years:
        data_dir = os.path.join(src_root, "data", year)
        print(f"→ Loading vector store from {data_dir}")
        load_data_vectostore(year, data_dir)
        
async def create_query_engines():
    """Tạo công cụ truy vấn cho từng năm sự kiện"""
    query_engine_tools = []
    for symbol in event_years:
        try:
            index = await load_indexs(symbol)  # Await để lấy index thực sự
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

    return query_engine_tools

async def chatbot_agent(text: str):
    """Xử lý câu hỏi người dùng với cơ chế fallback"""
    try:
        query_engine_tools = await create_query_engines()  # Await để lấy danh sách công cụ
        if not query_engine_tools:
            return "Xin lỗi, hệ thống đang cập nhật dữ liệu. Vui lòng thử lại sau."
        
        agent = ReActAgent.from_tools(
            tools=query_engine_tools,
            llm=llm_qwen25_3b,
            verbose=True
        )
        
        # Giả sử AGENT_QUERY_PROMPT được định nghĩa ở đâu đó
        formatted_prompt = TEXT_CORRECTION_PROMPT.format(text=text)
        response = agent.chat(formatted_prompt)  # Await nếu chat là async
        return str(response) if response else "Không tìm thấy thông tin liên quan"
    
    except Exception as e:
        logger.error(f"Lỗi xử lý câu hỏi: {str(e)}", exc_info=True)
        return "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."