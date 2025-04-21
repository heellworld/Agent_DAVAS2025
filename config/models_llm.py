import os
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
load_dotenv()

# Hoặc dùng biến môi trường (đúng tên biến)
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Khởi tạo LLM
llm_qwen25_3b = Ollama(model="qwen2.5:3b", temperature= 0, request_timeout=200.0)
llm_gemma_4b = Ollama(model="gemma3:4b", temperature= 0, request_timeout=300.0)
# ollama run gemma3:4b