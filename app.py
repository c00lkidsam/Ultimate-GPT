from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# ===== CONFIG =====
# Safe fallback: will use the key below if environment variable not set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"

MODEL = "gpt-3.5-turbo"

SYSTEM_PROMPT = """
You are ULTRA GPT.
You understand typos, simplify answers, explain clearly,
and respond intelligently like ChatGPT mixed with Gronk-level reasoning.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

LOGO_BG = "https://ih1.redbubble.net/image.5841016001.5391/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.u2.jpg"

# ===== UI =====
HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ULTRA GPT</title>
<style>
body {{
  margin: 0;
  font-family: system-ui;
  background: #343541;
  color: white;
  display: flex;
}}
#sidebar {{
  width: 220px;
  background: #202123;
  padding: 10px;
}}
#newChat {{
  width: 100%;
  padding: 12px;
  background: #444;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 15px;
}}
#chat {{
  flex: 1;
  display: flex;
  flex-direction: column;
}}
header {{
  height: 140px;
  background: url('{LOGO_BG}') center/cover no-repeat;
  display: flex;
  align-items: flex-end;
  padding: 15px;
  font-size: 28px;
  font-weight: bold;
  text-shadow: 0 0 10px black;
}}
#messages {{
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}}
.msg {{
  margin-bottom: 16px;
  white-space: pre-wrap;
}}
.user {{ color: #9cdcfe; }}
.bot {{ color: #dcdcaa; }}
#inputBox {{
  display: flex;
  padding: 12px;
  background: #40414f;
}}
input {{
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: none;
  outline: none;
}}
button {{
  background: #19c37d;
  border: none;
  padding: 12px;
  cursor: pointer;
}}
</style>
</head>

<body>
<div id="sidebar">
  <button id="newChat">+ New Chat</button>
</div>

<div id="chat">
  <header>ULTRA GPT</header>
  <div id="messages"></div>
  <div id="inputBox">
    <input id="input" placeholder="Message ULTRA GPT..." />
    <button onclick="send()">Send</button>
  </div>
</div>

<script>
function add(role, text) {{
  const d = document.createElement("div");
  d.className = "msg " + role;
  d.textContent = (role === "user" ? "You: " : "ULTRA GPT: ") + text;
  document.getElementById("messages").appendChild(d);
  d.scrollIntoView();
}}

async function send() {{
  const i = document.getElementById("input");
  if (!i.value) return;
  add("user", i.value);

  const r = await fetch("/chat", {{
    method: "POST",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify({{ message: i.value }})
  }});

  const j = await r.json();
  add("bot", j.reply);
  i.value = "";
}}

document.getElementById("newChat").onclick = async () => {{
  await fetch("/reset", {{ method: "POST" }});
  document.getElementById("messages").innerHTML = "";
}};
</script>
</body>
</html>
"""

# ===== ROUTES =====
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/reset", methods=["POST"])
def reset():
    global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"ok": True})

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_msg = request.json.get("message", "")
    messages.append({"role": "user", "content": user_msg})

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages
            },
            timeout=20
        )

        data = res.json()

        if "error" in data:
            reply = "OpenAI error: " + data["error"].get("message", "Unknown error")
        else:
            reply = data["choices"][0]["message"]["content"]

    except Exception as e:
        reply = "Server error: " + str(e)

    messages.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
