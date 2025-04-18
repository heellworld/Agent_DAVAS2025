import streamlit as st
import requests
import time

API_URL = "http://localhost:8000/api/chat"

# Lưu trữ lịch sử chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def chatbot_response(user_input):
    try:
        res = requests.post(API_URL, json={"message": user_input})
        if res.status_code == 200:
            return res.json().get("response", "Không có phản hồi từ chatbot.")
        else:
            return f"🚫 Lỗi: {res.status_code}"
    except Exception as e:
        return f"⚠️ Không kết nối được tới API: {e}"

st.set_page_config(page_title="Chatbot AI", layout="centered")
st.title("💬 Chatbot AI Davas Demo")
st.markdown("Gửi tin nhắn để trò chuyện với chatbot thông qua API.")

user_input = st.text_input("Bạn:", key="input")

if st.button("Gửi") and user_input.strip() != "":
    # 1. Thêm câu hỏi người dùng vào lịch sử
    st.session_state.chat_history.append(("🧑‍💻 Bạn", user_input))

    # 2. Hiển thị tạm phản hồi của bot với placeholder
    with st.spinner("🤖 Đang phân tích câu hỏi..."):
        response = chatbot_response(user_input)

    # 3. Thêm phản hồi từ bot sau khi có kết quả
    st.session_state.chat_history.append(("🤖 Chatbot", response))

# Hiển thị lịch sử chat (ngược dòng thời gian)
st.markdown("---")
for speaker, message in reversed(st.session_state.chat_history):
    st.markdown(f"**{speaker}:** {message}")
