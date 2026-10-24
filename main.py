# ============================================================
# main.py
# 作用：FastAPI 后端入口
# 运行：uvicorn main:app --reload
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

# 1. 创建 FastAPI 应用
app = FastAPI(
    title="AI 模拟面试官 API",
    description="AI 模拟面试官的后端接口，提供健康检查和聊天能力。",
)


# 首页：返回中文聊天页面
@app.get("/")
def index():
    return FileResponse("static/index.html")


# 2. 请求体：前端发来的 JSON
class ChatRequest(BaseModel):
    message: str


# 3. 响应体：返回给前端的 JSON
class ChatResponse(BaseModel):
    reply: str


# 4. 对话历史：先放一条 system 设定
#    现在是全局的，只适合单人演示；以后会改成按用户/会话保存
messages = [
    {"role": "system", "content": "你是一个简洁的面试教练，回答控制在三句话以内。"}
]


# 5. 健康检查
@app.get("/health", summary="健康检查")
def health():
    return {"status": "ok"}


# 6. 聊天接口：POST /chat
@app.post("/chat", summary="聊天", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 6.1 把用户的话追加进历史
    messages.append({"role": "user", "content": req.message})

    # 6.2 调用模型；出错时转成合适的 HTTP 状态码
    try:
        reply = ask(messages)
    except APITimeoutError:
        messages.pop()
        raise HTTPException(status_code=504, detail="模型响应超时，请重试。")
    except APIConnectionError:
        messages.pop()
        raise HTTPException(status_code=503, detail="无法连接模型服务，请稍后重试。")
    except AuthenticationError:
        messages.pop()
        raise HTTPException(status_code=500, detail="服务端 API Key 配置有误。")
    except RateLimitError:
        messages.pop()
        raise HTTPException(status_code=429, detail="请求太频繁，请稍后再试。")
    except APIStatusError:
        messages.pop()
        raise HTTPException(status_code=502, detail="模型服务返回错误，请稍后重试。")
    except Exception:
        messages.pop()
        raise HTTPException(status_code=500, detail="服务内部错误，请稍后重试。")

    # 6.3 模型返回空内容也当成错误
    if not reply:
        messages.pop()
        raise HTTPException(status_code=502, detail="模型返回了空内容，请重试。")

    # 6.4 把模型的回复也追加进历史
    messages.append({"role": "assistant", "content": reply})

    # 6.5 返回给前端
    return {"reply": reply}
