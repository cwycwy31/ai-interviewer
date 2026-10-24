# ============================================================
# app/chat/service.py
# 作用：聊天业务逻辑：读历史 -> 调模型 -> 存库
# ============================================================

from app.config import SYSTEM_PROMPT
from app.db.sqlite import load_messages, save_turn, clear_messages
from app.llm.client import ask


def handle_chat(message: str) -> str:
    # 1. 拼历史：system + 数据库里的历史 + 这次用户消息
    history = [{"role": "system", "content": SYSTEM_PROMPT}] + load_messages()
    history.append({"role": "user", "content": message})

    # 2. 调模型；异常交给上层处理
    reply = ask(history)

    # 3. 空回复当错误
    if not reply:
        raise ValueError("empty reply")

    # 4. 成功后才写库
    save_turn(message, reply)
    return reply


def get_history():
    return load_messages()


def reset_history():
    clear_messages()
