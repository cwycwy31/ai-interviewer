# ============================================================
# app/main.py
# 作用：FastAPI 入口
# 运行：uvicorn app.main:app --reload
# 页面：http://127.0.0.1:8000/
# ============================================================

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.chat.router import router as chat_router
from app.config import STATIC_DIR
from app.db.sqlite import init_db

# 1. 创建 FastAPI 应用
app = FastAPI(
    title="AI 模拟面试官 API",
    description="AI 模拟面试官的后端接口，提供健康检查、聊天和历史记录。",
)

# 2. 启动时建表
init_db()

# 3. 挂上聊天路由：/chat、/messages、/reset
app.include_router(chat_router)


# 4. 首页：返回中文聊天页面
@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


# 5. 健康检查
@app.get("/roadmap")
def roadmap():
    return FileResponse(STATIC_DIR / "roadmap.html")


@app.get("/health", summary="健康检查")
def health():
    return {"status": "ok"}
