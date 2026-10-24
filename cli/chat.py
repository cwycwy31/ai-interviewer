# ============================================================
# cli/chat.py
# 作用：命令行多轮聊天
# 运行：python -m cli.chat（在项目根目录）
# ============================================================

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError,
)

from app.config import SYSTEM_PROMPT
from app.llm.client import ask

# 调试开关：平时 False，只给用户看简短提示；排查问题时改成 True
DEBUG = False


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("你：")

        # 空输入直接跳过
        if not user_input.strip():
            continue

        # 退出
        if user_input.strip().lower() in ("exit", "quit", "再见"):
            print("再见。")
            break

        # 追加用户消息
        messages.append({"role": "user", "content": user_input})

        try:
            reply = ask(messages)

            if not reply:
                print("AI 返回了空内容，再试一次。")
                messages.pop()
                continue

            print("AI：", reply)
            messages.append({"role": "assistant", "content": reply})

        except APITimeoutError:
            print("请求超时。检查网络，或稍后再试。")
            messages.pop()
            continue
        except APIConnectionError:
            print("连不上服务器。检查网络/代理，或确认 base_url 是否正确。")
            messages.pop()
            continue
        except AuthenticationError:
            print("认证失败（401）。检查 .env 里的 DEEPSEEK_API_KEY 是否正确、有没有多余空格。")
            break
        except RateLimitError:
            print("请求太频繁（429）。等几秒再试。")
            messages.pop()
            continue
        except APIStatusError as e:
            print("请求失败，请稍后再试。")
            if DEBUG:
                print("[DEBUG]", e.status_code, "-", str(e))
            break
        except Exception as e:
            print("出了点意外，请稍后再试。")
            if DEBUG:
                print("[DEBUG]", type(e).__name__, "-", e)
            break


if __name__ == "__main__":
    main()
