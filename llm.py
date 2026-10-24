# ============================================================
# llm.py
# 作用：封装大模型调用，供 main.py / chat.py 使用
# 说明：只负责“把 messages 发给模型，拿回文字”，不处理 HTTP、不打印
# ============================================================

import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 读取 .env 里的 API Key
load_dotenv()

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
