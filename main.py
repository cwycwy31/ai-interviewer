# ============================================================
# main.py
# 作用：FastAPI 后端入口
# 运行：uvicorn main:app --reload
# 页面：http://127.0.0.1:8000/
# 文档：http://127.0.0.1:8000/docs
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError,
)

from llm import ask
from db import init_db, save_turn, load_messages, clear_messages

# 1. 创建 FastAPI 应用
app = FastAPI(
    title="AI 模拟面试官 API",
    description="AI 模拟面试官的后端接口，提供健康检查、聊天和历史记录。",
)

# 2. 启动时建表（表已存在就跳过）
init_db()

# 3. 系统设定：每次请求都放在历史最前面，不存数据库
SYSTEM_PROMPT = "你是一个简洁的面试教练，回答控制在三句话以内。"


# 4. 首页：返回中文聊天页面
@app.get("/")
def index():
    return FileResponse("static/index.html")


# 5. 请求体 / 响应体
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class Message(BaseModel):
    role: str
    content: str


class MessagesResponse(BaseModel):
    messages: list[Message]


# 6. 健康检查
@app.get("/health", summary="健康检查")
def health():
    return {"status": "ok"}


# 7. 读取历史
@app.get("/messages", response_model=MessagesResponse, summary="读取历史")
def get_messages():
    return {"messages": load_messages()}


# 8. 聊天接口
@app.post("/chat", summary="聊天", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 8.1 从数据库读历史，拼上 system 和这次用户消息
    history = [{"role": "system", "content": SYSTEM_PROMPT}] + load_messages()
    history.append({"role": "user", "content": req.message})

    # 8.2 调用模型；出错时转成合适的 HTTP 状态码
    try:
        reply = ask(history)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="模型响应超时，请重试。")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="无法连接模型服务，请稍后重试。")
    except AuthenticationError:
        raise HTTPException(status_code=500, detail="服务端 API Key 配置有误。")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="请求太频繁，请稍后再试。")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="模型服务返回错误，请稍后重试。")
    except Exception:
        raise HTTPException(status_code=500, detail="服务内部错误，请稍后重试。")

    # 8.3 空回复也当错误
    if not reply:
        raise HTTPException(status_code=502, detail="模型返回了空内容，请重试。")

    # 8.4 成功后才写入数据库：用户消息 + 模型回复
    save_turn(req.message, reply)

    # 8.5 返回给前端
    return {"reply": reply}


# 9. 清空历史
@app.post("/reset", summary="清空历史")
def reset():
    clear_messages()
    return {"status": "ok"}
