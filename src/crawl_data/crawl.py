import asyncio
import os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from llama_index.llms.ollama import Ollama
from llama_index.core.chat_engine import SimpleChatEngine
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

list_url = ["https://davas.vc/vi/"]


format_prompt = """
Bạn là chuyên gia định dạng lại nội dung báo cáo tiếng Việt. 
Yêu cầu:
1. Giữ nguyên 100% thông tin, không thêm/bớt nội dung
2. Sắp xếp thành các mục rõ ràng với tiêu đề in đậm
3. Sử dụng gạch đầu dòng cho các ý quan trọng
4. Chuẩn hóa chính tả và định dạng văn bản
5. Trình bày đẹp mắt, dễ đọc

Ví dụ format đầu ra:
**Tiêu đề chính**
- Mục 1: Nội dung chi tiết
- Mục 2: 
  + Tiểu mục 2.1: ...
  + Tiểu mục 2.2: ...

NỘI DUNG GỐC:
{text}
"""

async def crawl_and_save():
    """Thu thập nội dung từ các URL và lưu vào file .txt"""
    browser_conf = BrowserConfig(headless=True)
    run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        for url in list_url:
            filename = url.split('/')[-1] + '_raw.txt'  # Thêm hậu tố _raw để phân biệt
            logger.info(f"Đang thu thập dữ liệu từ: {url}")
            try:
                result = await crawler.arun(url=url, config=run_conf)
                if result.success:
                    result = result.markdown
                    logger.info(f"Đã thu thập xong nội dung từ {url}")
                    # Lưu nội dung vào file
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result)
                    logger.info(f"Đã lưu nội dung thô vào: {filename}")
                else:
                    logger.error(f"Thu thập dữ liệu thất bại từ {url}: {result.error_message}")
            except Exception as e:
                logger.error(f"Lỗi khi thu thập dữ liệu từ {url}: {e}")


async def main():
    await crawl_and_save()

if __name__ == "__main__":
    asyncio.run(main())