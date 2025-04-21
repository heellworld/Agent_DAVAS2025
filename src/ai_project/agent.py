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
Bạn là chuyên viên hỗ trợ khách hàng tại sự kiện Danang Venture and Angel Summit.
Và nhiệm vụ của bạn sẽ là xử lý câu hỏi theo quy trình sau:

1. **Xử lý câu hỏi:**
    - Kiểm tra và bóc tách ra vấn đề chính, chỉ nên tập trung vào nội dung chính mà người dùng muốn đề cập/yêu cầu thông tin
    - Không quan tâm tới các thông tin thêm của người dùng như: "Bạn hãy cho tôi biết ...", "Tôi muốn biết ...", "Tôi có thể hỏi bạn một câu hỏi không?"
    - Nếu câu hỏi không rõ ràng, hãy yêu cầu người dùng cung cấp thêm thông tin hoặc làm rõ câu hỏi của họ.

2. **Xử lý chọn công cụ truy vấn**
    - Nếu người dùng hỏi về thông tin các đơn vị startup khởi nghiệp, gọi vốn, startup thuyết trình về đầu tư thì sẽ sử dụng công cụ "Startupfundraising_companys2025"
    - Nếu người dùng hỏi về thông tin các đơn vị cho vốn, Funding, Investment, Quỹ đầu tư, nhà đầu tư thì sẽ sử dụng công cụ "InvestmentFunds_companys2025"
    - Nếu người dùng muốn biết về thông tin chương trình, lịch trình sự kiện, các thông tin liên hệ, thông tin khác sẽ sử dụng công cụ "Davas2025"
    - Nếu ngươi dùng muốn biết về thông tin về chương trình trước đây, năm 2024 sẽ sử dụng công cụ "Davas2024"

**LƯU Ý QUAN TRỌNG:**
    - Nếu người dùng cần đăng ký tham gia gọi vốn tại DAVAS thì đưa đường link sau: "https://docs.google.com/forms/d/e/1FAIpQLSce4Bexdg9_fBrsfqvnlwQM9AATq-rW_zD5Y7Ob3eDD47K9NA/viewform"
    - Khi xử lý truy vấn hoặc sinh câu trả lời, hãy sử dụng bảng từ đồng nghĩa sau để nhận diện và mở rộng các khái niệm liên quan, bao gồm cả tiếng Việt và tiếng Anh, đảm bảo mọi từ đồng nghĩa đều được hiểu là cùng một concept.
    - Sử dụng thông tin từ tài liệu hoặc phản hồi xã giao phù hợp. Trả lời theo ngôn ngữ câu hỏi của người dùng.
    - Không được tự tìm kiếm/thêm thông tin khác từ bạn, chỉ sử dụng thông tin có trong tài liệu, kiến thức của tôi đã cung cấp

CÂU HỎI: {text}
"""

# Danh sách các sự kiện cần xử lý
event_years = ["Davas2024", "Davas2025"]

async def initialize_vector_stores():
    """Khởi tạo vector store cho các năm sự kiện"""
    # insert_file("Davas2024", r"D:\project_company\Agent_DAVAS2025\src\data\Davas2024")
    await load_data_vectostore("Davas2025", r"D:\project_company\Agent_DAVAS2025\src\data\Davas2025")
    await load_data_vectostore("Startupfundraising_companys2025", r"D:\project_company\Agent_DAVAS2025\src\data\Startup")
    await load_data_vectostore("InvestmentFunds_companys2025", r"D:\project_company\Agent_DAVAS2025\src\data\QuyDauTu")

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

    try:
        index_fundraising = await load_indexs("Startupfundraising_companys2025")
        index_funding = await load_indexs("InvestmentFunds_companys2025")
        
        query_engine_fundraising = index_fundraising.as_query_engine(
            similarity_top_k=5,
            llm=llm_qwen25_3b,
            response_mode="compact"
        )
        tool_fundraising = QueryEngineTool.from_defaults(
            query_engine=query_engine_fundraising,
            name="Startupfundraising_companys2025",
            description="Dữ liệu chi tiết về các công ty gọi vốn và startup"
        )
        query_engine_tools.append(tool_fundraising)
        
        query_engine_funding = index_funding.as_query_engine(
            similarity_top_k=5,
            llm=llm_qwen25_3b,
            response_mode="compact"
        )
        tool_funding = QueryEngineTool.from_defaults(
            query_engine=query_engine_funding,
            name="InvestmentFunds_companys2025",
            description="Dữ liệu chi tiết về các công ty cho vốn và quỹ đầu tư"
        )
        query_engine_tools.append(tool_funding)
    except Exception as e:
        logger.warning(f"Không tải được công cụ cho công ty: {str(e)}")

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
        
        # Giả sử TEXT_CORRECTION_PROMPT được định nghĩa ở đâu đó
        formatted_prompt = TEXT_CORRECTION_PROMPT.format(text=text)
        response = agent.chat(formatted_prompt)  # Await nếu chat là async
        return str(response) if response else "Không tìm thấy thông tin liên quan"
    
    except Exception as e:
        logger.error(f"Lỗi xử lý câu hỏi: {str(e)}", exc_info=True)
        return "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."