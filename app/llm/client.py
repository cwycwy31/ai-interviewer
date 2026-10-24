# ============================================================
# app/llm/client.py
# 作用：封装大模型调用
# 说明：只负责“把 messages 发给模型，拿回文字”
# ============================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

from app.config import BASE_DIR

# 1. 读取项目根目录的 .env
load_dotenv(BASE_DIR / ".env")

# 2. 创建客户端，指向 DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# 3. 模型名
MODEL = "deepseek-v4-flash"


# 4. 对外提供的方法：传对话历史，返回回复正文
def ask(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return response.choices[0].message.content
