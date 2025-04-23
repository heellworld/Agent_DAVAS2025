import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import nest_asyncio
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import ReActAgent
from config.models_llm import llm_gemini
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

DAVAS (Danang Venture and Angel Summit) là Diễn đàn gọi vốn đầu tư Thiên Thần và Mạo Hiểm được tổ chức thường niên tại thành phố Đà Nẵng, khởi đầu từ năm 2024, với các mục tiêu chính:
- Định vị Đà Nẵng trở thành điểm đến đầu tư và gọi vốn quốc tế.
- Xây dựng cộng đồng nhà đầu tư thiên thần và quỹ đầu tư mạo hiểm tại Đà Nẵng.
- Tạo sân chơi để dự án và doanh nghiệp khởi nghiệp đổi mới sáng tạo (ĐMST) tiếp cận nhà đầu tư, quỹ đầu tư và chuyên gia đầu ngành.

Hoạt động chính của sự kiện Davas 2025 gồm:
Tổ chức gây quỹ và kết nối 1:1 cho hơn 30 dự án và khởi nghiệp đổi mới sáng tạo với các nhà đầu tư và quỹ đầu tư; Ra mắt không gian đổi mới Đà Nẵng - Hồng Kông; Thăm và làm việc tại các không gian đổi mới tại Đà Nẵng.

Nhiệm vụ của bạn sẽ là xử lý câu hỏi theo quy trình sau:

1. **Xử lý câu hỏi:**
    - Kiểm tra và bóc tách ra vấn đề chính, chỉ nên tập trung vào nội dung chính mà người dùng muốn đề cập/yêu cầu thông tin
    - Không quan tâm tới các thông tin thêm của người dùng như: "Bạn hãy cho tôi biết ...", "Tôi muốn biết ...", "Tôi có thể hỏi bạn một câu hỏi không?"
    - Nếu câu hỏi không rõ ràng, hãy yêu cầu người dùng cung cấp thêm thông tin hoặc làm rõ câu hỏi của họ.

2. **Xử lý câu hỏi thông tin:** (Mặc định sẽ sử dụng Davas2025 nếu người dùng không đề cập đến năm sự kiện muốn biết)
   - Xác định năm sự kiện liên quan
   - Sử dụng công cụ truy vấn tương ứng (Davas2024/Davas2025)
   - Cung cấp thông tin chính xác, ngắn gọn từ tài liệu
   - Nếu liên quan cả hai năm, so sánh thông tin từ cả hai nguồn

**PHÂN BIỆT RÕ RÀNG GIỮA BÊN GỌI VỐN VÀ BÊN CUNG CẤP VỐN:**
1. **Đơn vị/nhà gọi vốn (Startups/Doanh nghiệp khởi nghiệp):**
   - Đây là các công ty/dự án khởi nghiệp ĐANG TÌM KIẾM vốn đầu tư
   - Trong tài liệu, thuộc mục "CÁC ĐƠN VỊ STARTUP VÀ GỌI VỐN Tại DAVAS 2025"
   - Bao gồm 13 đơn vị: EM&AI, UCTalent, Hạt Khử Mùi ENSO, FASTDO, E-Rent, Tripin, Alpha Asimov Robotics, 5 SAO, Chợ Cà Phê, HanaGold, Augmented Hype, Run Together, DDC Holdings

2. **Đơn vị/nhà cung cấp vốn (Quỹ đầu tư/Nhà đầu tư):**
   - Đây là các quỹ đầu tư, nhà đầu tư thiên thần ĐANG TÌM KIẾM dự án để đầu tư
   - Trong tài liệu, thuộc mục "Thông tin về Quỹ đầu tư và các đối tác"
   - Bao gồm 17 đơn vị: Quest Ventures, Do Ventures, ThinkZone Ventures, FUNDGO, WeAngels Capital Ventures, Vertex Ventures, TRIVE, Summit Capital, Genesia Ventures, Daiwa Corporate Investment, Kilsa Global, Sunwah Innovation Center, Makara Capital, JN Capital & Growth Advisory

**BẢNG TỪ ĐỒNG NGHĨA VÀ PHÂN LOẠI:**
- Bên gọi vốn = startup = doanh nghiệp khởi nghiệp = công ty khởi nghiệp = dự án gọi vốn = đơn vị gọi vốn = doanh nghiệp đổi mới sáng tạo = dự án cần vốn
- Bên cung cấp vốn = quỹ đầu tư = nhà đầu tư = angel investor = venture capital = quỹ mạo hiểm = đơn vị tài trợ = đối tác đầu tư = nhà đầu tư thiên thần

**CÁC MẪU CÂU HỎI THƯỜNG GẶP VÀ CÁCH XỬ LÝ:**

1. **Câu hỏi về bên gọi vốn (startups):**
- "Các công ty/startup gọi vốn tại DAVAS 2025 là những ai/gồm những đơn vị nào?"
   - "Có những dự án nào đang gọi vốn tại sự kiện?"
   - "Danh sách các startup tham gia DAVAS 2025?"
   - "Các doanh nghiệp khởi nghiệp tham gia sự kiện là ai?"
   
   → Trả lời bằng thông tin từ mục "CÁC ĐƠN VỊ STARTUP VÀ GỌI VỐN Tại DAVAS 2025"

2. **Câu hỏi về bên cung cấp vốn (quỹ đầu tư):**
   - "Các quỹ đầu tư tham gia DAVAS 2025 là những ai/gồm những đơn vị nào?"
   - "Có những nhà đầu tư nào tham gia sự kiện?"
   - "Danh sách các quỹ mạo hiểm tại DAVAS 2025?"
   - "Các nhà đầu tư thiên thần tham gia sự kiện là ai?"
   
   → Trả lời bằng thông tin từ mục "Thông tin về Quỹ đầu tư và các đối tác"

3. **Câu hỏi chi tiết về một startup cụ thể:**
   - "Cho tôi biết thông tin về EM&AI?"
   - "UCTalent là công ty gì?"
   - "Dự án Chợ Cà Phê làm gì?"
   
   → Trả lời chi tiết từ phần mô tả tương ứng trong mục "CÁC ĐƠN VỊ STARTUP VÀ GỌI VỐN"

4. **Câu hỏi chi tiết về một quỹ đầu tư cụ thể:**
   - "Quest Ventures là gì?"
   - "Cho tôi biết về FUNDGO?"
   - "Sunwah Innovation Center hoạt động trong lĩnh vực nào?"
   
   → Trả lời chi tiết từ phần mô tả tương ứng trong mục "Thông tin về Quỹ đầu tư và các đối tác"

**LƯU Ý QUAN TRỌNG:** 
- Nếu người dùng cần đăng ký tham gia gọi vốn thì đưa đường link sau: "https://docs.google.com/forms/d/e/1FAIpQLSce4Bexdg9_fBrsfqvnlwQM9AATq-rW_zD5Y7Ob3eDD47K9NA/viewform"
- Khi xử lý truy vấn hoặc sinh câu trả lời, hãy sử dụng bảng từ đồng nghĩa đã cung cấp để nhận diện và mở rộng các khái niệm liên quan, đảm bảo mọi từ đồng nghĩa đều được hiểu là cùng một concept.
- Trả lời theo ngôn ngữ câu hỏi của người dùng.
- Không được tự tìm kiếm thêm thông tin khác từ bạn, chỉ sử dụng thông tin có trong tài liệu, kiến thức đã cung cấp.
- Khi người dùng hỏi về "gọi vốn" hoặc "startup", luôn hiểu đó là các doanh nghiệp ĐANG TÌM KIẾM vốn đầu tư, không phải các quỹ đầu tư.
- Khi người dùng hỏi về "quỹ đầu tư" hoặc "nhà đầu tư", luôn hiểu đó là các đơn vị ĐANG CUNG CẤP vốn đầu tư.
- BẮT BUỘC THÔNG TIN QUAN TRỌNG NHƯ: LỊCH TRÌNH, CHƯƠNG TRÌNH, CÁC KHÁCH MỜI/CHUYÊN GIA PHẢI CUNG CẤP HẦU NHƯ TOÀN BỘ THÔNG TIN ĐẦY ĐỦ NHẤT.

CÂU HỎI: {text}
"""

event_years = ["Davas2024", "Davas2025"]

def initialize_vector_stores():
    # __file__ là …\src\ai_project\agent.py
    base_path = os.path.dirname(os.path.abspath(__file__))      # …\src\ai_project
    src_root  = os.path.dirname(base_path)                      # …\src

    for year in ["Davas2025"]:
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
                similarity_top_k=10,
                llm=llm_gemini,
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
            llm=llm_gemini,
            verbose=True
        )
        
        # Giả sử AGENT_QUERY_PROMPT được định nghĩa ở đâu đó
        formatted_prompt = TEXT_CORRECTION_PROMPT.format(text=text)
        response = agent.chat(formatted_prompt)  # Await nếu chat là async
        return str(response) if response else "Không tìm thấy thông tin liên quan"
    
    except Exception as e:
        logger.error(f"Lỗi xử lý câu hỏi: {str(e)}", exc_info=True)
        return "Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."