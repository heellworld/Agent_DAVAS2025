# Davas Chatbot API

API chatbot cung cấp thông tin về sự kiện Danang Venture and Angel Summit (DAVAS) các năm 2024 và 2025.

## Yêu cầu hệ thống

*   Python 3.9+
*   Pip (trình quản lý gói Python)
*   Ollama (để chạy mô hình ngôn ngữ cục bộ)

## Cài đặt

1.  **Clone repository (nếu chưa có):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
    ```bash
    python -m venv venv
    # Trên Windows
    .\venv\Scripts\activate
    # Trên macOS/Linux
    source venv/bin/activate
    ```

3.  **Cài đặt các thư viện Python cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cài đặt và chạy Ollama:**
    *   Truy cập [https://ollama.com/](https://ollama.com/) và làm theo hướng dẫn cài đặt cho hệ điều hành của bạn.
    *   Sau khi cài đặt, tải mô hình ngôn ngữ được sử dụng trong dự án (ví dụ: Qwen 2.5 3B nếu bạn đang dùng `llm_qwen25_3b`):
        ```bash
        ollama pull qwen2:1.5b 
        ```
        *(Lưu ý: Thay `qwen2:1.5b` bằng tên mô hình chính xác bạn đang sử dụng trong `config/models_llm.py` nếu khác)*
    *   Đảm bảo Ollama đang chạy nền.

5.  **(Tùy chọn) Cấu hình biến môi trường:**
    *   Nếu dự án của bạn sử dụng các API key hoặc cấu hình nhạy cảm khác (ví dụ: key OpenAI), hãy tạo file `.env` trong thư mục gốc và định nghĩa chúng theo mẫu trong file `.env.example` (nếu có).

## Khởi tạo dữ liệu (Chạy lần đầu)

Trước khi chạy API, bạn cần khởi tạo cơ sở dữ liệu vector. Mở file `main.py` và bỏ comment (xóa dấu `#`) khỏi các dòng sau:

```python
# main.py

# ... (các import)

if __name__ == "__main__":
    # Khởi tạo vector stores trước khi bắt đầu
    try:
        print("Đang khởi tạo dữ liệu, vui lòng chờ...")
        initialize_vector_stores() # Đảm bảo hàm này được gọi
        print("Khởi tạo dữ liệu thành công!")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo dữ liệu: {str(e)}")
        exit(1)

    # ... (phần chạy uvicorn)
```

Sau đó chạy lệnh:

```bash
python main.py
```

Quá trình này có thể mất một lúc tùy thuộc vào khối lượng dữ liệu. Sau khi hoàn tất và thông báo "Khởi tạo dữ liệu thành công!", bạn có thể comment lại các dòng đó trong `main.py` để không chạy lại mỗi lần khởi động server.

## Chạy API Server

Sau khi đã cài đặt và khởi tạo dữ liệu:

```bash
python main.py
```

Server API sẽ khởi động và lắng nghe tại `http://0.0.0.0:8000`.

## Sử dụng API

Bạn có thể gửi yêu cầu POST đến endpoint `/api/chat` để tương tác với chatbot.

**Ví dụ sử dụng cURL:**

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Thông tin về diễn giả DAVAS 2025?"}'
```

**Ví dụ sử dụng Python (với thư viện `requests`):**

```python
import requests
import json

url = "http://localhost:8000/api/chat"
payload = json.dumps({"query": "Sự kiện DAVAS 2024 tổ chức ở đâu?"})
headers = {'Content-Type': 'application/json'}

response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200:
    print("Phản hồi từ Bot:")
    print(response.json().get('response'))
else:
    print(f"Lỗi: {response.status_code}")
    print(response.text)

```

Bạn cũng có thể truy cập `http://localhost:8000/docs` trong trình duyệt để xem giao diện Swagger UI và thử nghiệm API trực tiếp. 