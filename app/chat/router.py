# ============================================================
# app/chat/router.py
# 作用：聊天相关的 HTTP 路由
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError,
)

from app.chat.service import handle_chat, get_history, reset_history

router = APIRouter()


# 请求体 / 响应体
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class Message(BaseModel):
    role: str
    content: str


class MessagesResponse(BaseModel):
    messages: list[Message]


# 读取历史
@router.get("/messages", response_model=MessagesResponse, summary="读取历史")
def messages():
    return {"messages": get_history()}


# 聊天
@router.post("/chat", summary="聊天", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        reply = handle_chat(req.message)
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
    except ValueError:
        raise HTTPException(status_code=502, detail="模型返回了空内容，请重试。")
    except Exception:
        raise HTTPException(status_code=500, detail="服务内部错误，请稍后重试。")

    return {"reply": reply}


# 清空历史
@router.post("/reset", summary="清空历史")
def reset():
    reset_history()
    return {"status": "ok"}
