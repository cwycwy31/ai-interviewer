# ============================================================
# main.py
# 作用：FastAPI 后端入口
# 运行：uvicorn main:app --reload
# 测试：http://127.0.0.1:8000/health
# ============================================================

from fastapi import FastAPI

# 创建 FastAPI 应用，起名 app
app = FastAPI(title="AI 模拟面试官 API")


# 定义一个 GET 接口：/health
@app.get("/health")
def health():
    # 返回 dict，FastAPI 会自动转成 JSON
    return {"status": "ok"}
