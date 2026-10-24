# ============================================================
# app/config.py
# 作用：集中放路径和常量
# ============================================================

from pathlib import Path

# 项目根目录：app/config.py -> app/ -> 项目根
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "chat.db"
STATIC_DIR = BASE_DIR / "static"

# 系统设定：每次请求都放在历史最前面，不存数据库
SYSTEM_PROMPT = "你是一个简洁的面试教练，回答控制在三句话以内。"
