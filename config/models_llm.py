import os
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
# from llama_index.llms.gemini import Gemini
load_dotenv()

# # Hoặc dùng biến môi trường (đúng tên biến)
# gemini_api_key = os.getenv("GEMINI_API_KEY")

# Khởi tạo LLM
llm_qwen25_3b = Ollama(model="qwen2.5:3b", temperature= 0, request_timeout=200.0)
llm_gemma_4b = Ollama(model="gemma3:4b", temperature= 0, request_timeout=300.0)
# llm_gemini = Gemini(model="models/gemini-2.0-flash-lite")
