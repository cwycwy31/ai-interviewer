# ============================================================
# chat.py
# 作用：命令行多轮聊天，模型能记住前面说过的话，并能处理常见接口错误
# 流程：读配置 -> 建客户端 -> 循环（读输入 -> 追加历史 -> 发请求 -> 打印 -> 追加回复）
# 运行：python chat.py，输入 exit / quit / 再见 退出
# ============================================================

# 1. 导入工具
import os
from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
    APIStatusError,
)

# 调试开关：平时 False，只给用户看简短提示；排查问题时改成 True
DEBUG = False

# 2. 读取 .env 里的 API Key
load_dotenv()

# 3. 创建客户端，指向 DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# 4. 对话历史：放在循环外面，才能一直累积
#    第一条 system 是给模型的设定，不是你说的话
messages = [
    {"role": "system", "content": "你是一个简洁的面试教练，回答控制在三句话以内。"}
]

# 5. 主循环
while True:
    user_input = input("你：")

    # 5.1 空输入直接跳过，避免发空消息
    if not user_input.strip():
        continue

    # 5.2 退出：输入 exit / quit / 再见 都行
    if user_input.strip().lower() in ("exit", "quit", "再见"):
        print("再见。")
        break

    # 5.3 把你这次说的话追加进历史
    messages.append({"role": "user", "content": user_input})

    # 5.4 发请求，并处理常见错误
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
        )

        # 5.5 先检查返回结构，再取正文
        if not response.choices:
            print("AI 没有返回结果，再试一次。")
            messages.pop()          # 撤回这次提问，避免污染历史
            continue

        reply = response.choices[0].message.content
        if not reply:
            print("AI 返回了空内容，再试一次。")
            messages.pop()
            continue

        print("AI：", reply)

        # 5.6 把模型回复也追加进历史
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
        # 给用户看的：短、能行动，不打印原始 JSON
        if e.status_code == 400:
            print("请求参数有问题，请检查模型名或消息格式。")
        elif e.status_code == 402:
            print("余额不足，请先充值。")
        elif e.status_code == 404:
            print("接口地址不对，请检查 base_url。")
        elif e.status_code >= 500:
            print("服务器暂时出问题，请稍后再试。")
        else:
            print("请求失败，请稍后再试。")

        # 给开发者看的：完整错误只在 DEBUG 打开时显示
        if DEBUG:
            print("[DEBUG]", e.status_code, "-", str(e))
        break
    except Exception as e:
        print("出了点意外，请稍后再试。")
        if DEBUG:
            print("[DEBUG]", type(e).__name__, "-", e)
        break
