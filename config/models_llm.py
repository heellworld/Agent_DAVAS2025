from llama_index.llms.ollama import Ollama


# Khởi tạo LLM
llm_qwen25_3b = Ollama(model="qwen2.5:3b", request_timeout=200.0)