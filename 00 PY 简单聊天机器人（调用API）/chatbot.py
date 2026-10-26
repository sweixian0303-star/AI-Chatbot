import os                    # 内置库，用于检查文件是否存在
import json                  # 内置库，用于读写 JSON 格式的对话历史
from datetime import datetime  # 暂时未用到，可用于记录消息时间戳
from groq import Groq        # Groq 官方库，用于调用 AI 模型

# 初始化 Groq 客户端，传入 API Key 进行身份验证
client = Groq(api_key="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")

# System Prompt：定义 AI 的人设和行为规则
# 这段话会在每次对话时偷偷发给 AI，用户看不到，但 AI 会遵守
SYSTEM_PROMPT = """你是一个友善，聪明的AI助手 名字叫「西瓜」
你的特点：
- 用中文回答（除非用户用英文问）
- 回答简洁清晰，不过度啰嗦
- 有礼貌，偶尔幽默
- 记住用户说过的信息，在对话中自然引用
"""

# 对话历史保存的文件名，跟 chatbot.py 在同一个文件夹
HISTORY_FILE = "chat_history.json"

# ---- 文件读写 ----

def load_history():
    """从 JSON 文件读取上次的对话历史，文件不存在则返回空列表"""
    if not os.path.exists(HISTORY_FILE):  # 第一次运行时文件还没有
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)               # 把 JSON 解析成 Python 列表

def save_history(history):
    """把对话历史列表写入 JSON 文件"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        # ensure_ascii=False：中文正常保存，不变成 \u4e2d\u6587
        # indent=2：格式化缩进，文件更易读
    print(f"对话已保存到 {HISTORY_FILE}")

# ---- 核心功能 ----

def chat(history):
    """把对话历史发给 AI，返回 AI 的回复文字"""
    # system prompt 放在最前面，告诉 AI 它是谁
    # 后面跟着完整的对话历史，让 AI 知道上下文
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # 使用的模型名称
        messages=messages,
        max_tokens=1024,               # 限制回复最长 1024 个 token，防止回复过长
        temperature=0.7,               # 创意度：0 = 保守死板，1 = 天马行空，0.7 是平衡点
    )
    # choices[0] 是第一个回复（通常只有一个），.message.content 是文字内容
    return response.choices[0].message.content

def show_help():
    """打印所有可用指令"""
    print("""
        指令列表：
        /help    - 显示这个帮助
        /clear   - 清除对话记忆
        /save    - 保存对话历史
        /load    - 读取上次对话
        /history - 显示当前对话历史
        quit     - 退出程序
    """)

def show_history(history):
    """打印当前对话历史，每条只显示前 80 个字符"""
    if not history:
        print("  （目前没有对话记录）\n")
        return
    print("\n--- 对话历史 ---")
    for msg in history:
        # 根据 role 判断是用户还是 AI
        role = "你" if msg["role"] == "user" else "🍉 西瓜"
        print(f"  {role}：{msg['content'][:80]}...")  # [:80] 只取前 80 字
    print("--- 结束 ---\n")

# ---- 主程序 ----

def main():
    print("=" * 40)
    print("🍉 西瓜 AI 助手")
    print("输入 /help 查看指令，quit 退出")
    print("=" * 40 + "\n")

    history = []  # 存放本次对话的所有消息

    while True:
        user_input = input("你：").strip()  # strip() 去掉首尾空格

        if not user_input:         # 空输入直接跳过
            continue

        # 退出：先自动保存再退出
        if user_input.lower() == "quit":
            save_history(history)
            print("👋 再见！")
            break

        # 显示帮助（注意：需要加 /，避免和普通消息冲突）
        if user_input == "/help":
            show_help()
            continue

        # 清除记忆：把 history 列表清空
        if user_input == "/clear":
            history = []
            print("✅ 记忆已清除\n")
            continue

        # 手动保存对话
        if user_input == "/save":
            save_history(history)
            continue

        # 读取上次保存的对话历史
        if user_input == "/load":
            history = load_history()
            print(f"✅ 已读取 {len(history)} 条历史记录\n")
            continue

        # 显示当前对话历史
        if user_input == "/history":
            show_history(history)
            continue

        # 普通对话：把用户消息加入历史，发给 AI，把回复也加入历史
        history.append({"role": "user", "content": user_input})

        try:
            reply = chat(history)
            history.append({"role": "assistant", "content": reply})
            print(f"\n🍉 西瓜：{reply}\n")

        except Exception as e:
            print(f"❌ 出错了：{e}\n")
            history.pop()  # 出错时移除刚加的用户消息，保持历史记录干净

# 只有直接运行 chatbot.py 才执行 main()
# 被其他文件 import 时不会自动执行
if __name__ == "__main__":
    main()