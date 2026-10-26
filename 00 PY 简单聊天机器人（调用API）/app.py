from flask import Flask, request, jsonify, render_template, session
# Flask        — 创建网页应用
# request      — 读取用户发来的 HTTP 请求数据
# jsonify      — 把 Python 字典转成 JSON 格式返回给前端
# render_template — 渲染 HTML 模板文件
# session      — 服务器端的临时存储，用来记住每个用户的对话历史
from groq import Groq  # Groq 官方库，用于调用 AI 模型
import os              # 内置库，这里备用（如读取环境变量）

# 创建 Flask 应用实例，__name__ 告诉 Flask 当前文件的位置
app = Flask(__name__)

# session 加密密钥，随便填一段字符串即可
# 生产环境应该用随机生成的复杂字符串，不要写死
app.secret_key = "watermelon_secret_key"

# 初始化 Groq 客户端，传入 API Key 进行身份验证
client = Groq(api_key="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")

# System Prompt：定义 AI 的人设，每次对话都会带上这段话
# 用户看不到，但 AI 会遵守这些规则
SYSTEM_PROMPT = """你是一个友善，聪明的AI助手，名字叫「🍉西瓜」
你的特点：
- 用中文回答（除非用户用英文）
- 回答简洁清晰，不过度啰嗦
- 有礼貌，偶尔幽默
- 记住用户说过的消息，在对话中自然引用
"""

# ---- 路由（Route）----
# 路由就是 URL 和函数的对应关系
# 用户访问某个 URL，Flask 就调用对应的函数

@app.route("/")                    # 用户访问 http://127.0.0.1:5000/ 时触发
def index():
    """返回主页 HTML"""
    session.setdefault("history", [])  # 如果 session 里还没有 history，初始化为空列表
    return render_template("index.html")  # 渲染 templates/index.html 并返回给浏览器

@app.route("/chat", methods=["POST"])  # 只接受 POST 请求（前端发消息用 POST）
def chat():
    """接收前端发来的用户消息，调用 AI，返回回复"""
    data       = request.get_json()              # 解析前端发来的 JSON 数据
    user_input = data.get("message", "").strip() # 取出 message 字段，去掉首尾空格

    # 空消息直接返回错误，400 = Bad Request（客户端请求有问题）
    if not user_input:
        return jsonify({"error": "消息不能为空"}), 400

    # 从 session 读取这个用户的对话历史
    history = session.get("history", [])
    history.append({"role": "user", "content": user_input})  # 把用户消息加入历史

    try:
        # system prompt 放最前面，后面跟完整对话历史
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # 使用的模型
            messages=messages,
            max_tokens=1024,               # 限制回复长度
            temperature=0.7,               # 创意度，0.7 是保守和创意的平衡点
        )

        reply = response.choices[0].message.content  # 取出 AI 回复的文字

        history.append({"role": "assistant", "content": reply})  # 把 AI 回复也加入历史
        session["history"] = history  # 把更新后的历史存回 session

        # 200 = OK，表示请求成功，把回复以 JSON 格式返回给前端
        return jsonify({"reply": reply}), 200

    except Exception as e:
        history.pop()                      # 出错时移除刚加的用户消息，保持历史干净
        return jsonify({"error": str(e)}), 500  # 500 = 服务器内部错误

@app.route("/clear", methods=["POST"])  # 只接受 POST 请求
def clear():
    """清除当前用户的对话历史"""
    session["history"] = []              # 把 session 里的历史重置为空列表
    return jsonify({"status": "ok"})     # 返回成功状态给前端

# 直接运行 app.py 时启动 Flask 开发服务器
# debug=True：代码改动后自动重启，并显示详细错误信息（上线时要改成 False）
if __name__ == "__main__":
    app.run(debug=True)