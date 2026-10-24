# ============================================================
# app/db/sqlite.py
# 作用：SQLite 数据库，保存对话历史
# 说明：只负责读写数据库
# ============================================================

import sqlite3
from contextlib import closing

from app.config import DB_PATH


# 1. 建立数据库连接
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# 2. 建表：第一次运行自动创建
def init_db():
    with closing(get_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        conn.commit()


# 3. 保存一轮对话：用户的话 + 模型的回复，放在同一个事务里
def save_turn(user_content, assistant_content):
    with closing(get_connection()) as conn:
        conn.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            ("user", user_content),
        )
        conn.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            ("assistant", assistant_content),
        )
        conn.commit()


# 4. 读取最近 limit 条消息，按时间正序返回
def load_messages(limit=50):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM (
                SELECT id, role, content FROM messages ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
            """,
            (limit,),
        ).fetchall()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


# 5. 清空历史
def clear_messages():
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM messages")
        conn.commit()
