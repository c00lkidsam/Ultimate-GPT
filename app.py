from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Use your OpenAI API key (replace with your key or use env variable)
API_KEY = os.getenv("OPENAI_API_KEY", "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").strip()

SYSTEM_PROMPT = """
You are Sam GPT, a highly intelligent AI assistant.
- Can understand typos and simplify language.
- Can explain concepts, code, research, and reason like Gronk.
- Very friendly, clear, helpful.
- NEVER respond with NSFW or hate content.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
MAX_MESSAGES = 15

HAWK_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/1/12/Hawk_icon.png"

HTML_UI = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sam GPT Pro Gronk</title>
<style>
body {{
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #0a0a0a;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
}}
#header {{
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}}
#logo {{ width: 50px; height: 50px; margin-right: 10px; }}
#title {{ font-size: 24px; font-weight: bold; color: #00c6ff; }}
#chat {{
  max-width: 600px;
  width: 100%;
  height: 70vh;
  overflow-y: auto;
  padding: 10px;
  background: #1a1a1a;
  border-radius: 10px;
  box-shadow: 0 0 25px rgba(0,255,255,0.3);
}}
.message {{
  padding: 12px;
  margin: 6px 0;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
  font-size: 16px;
}}
.user {{
  background: linear-gradient(120deg, #ff6a00, #ee0979);
  text-align: right;
  color: #fff;
  margin-left: auto;
}}
.bot {{
  background: linear-gradient(120deg, #00c6ff, #0072ff);
  text-align: left;
  color: #fff;
  margin-right: auto;
}}
#input-area {{
  display: flex;
  margin-top: 10px;
  width: 100%;
  max-width: 600px;
}}
#userInput {{
  flex: 1;
  padding: 12px;
  border-radius: 8px 0 0 8px;
  border: none;
  outline: none;
  font-size: 16px;
}}
button {{
  padding: 12px;
  background: #ff6a00;
  border: none;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  border-radius: 0 8px 8px 0;
  transition: all 0.2s ease;
}}
button:hover {{ background: #ee0979; }}
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-thumb {{ background: #ff6a00; border-radius: 4px; }}
</style>
</head>
<body>
<div id="header">
  <img src="{HAWK_LOGO_URL}" alt="Hawk Logo" id="logo">
  <div id="title">Sam GPT Pro Gronk</div>
</div>
<div id="chat"></div>
<div id="input-area">
  <input type="text" id="userInput" placeholder="Type your message...">
  <button>Send</button>
</div>
<script>
window.onload = function() {{
  async function sendMessage() {{
    const input = document.getElementById("userInput");
    const message = input.value;
    if(!message) return;
    addMessage(message,'user');
    input.value='';
    try {{
      const res = await fetch('/chat', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{message}})
      }});
      const data = await res.json();
      addMessage(data.reply,'bot');
    }} catch(err) {{
      addMessage("Server error, try again later.","bot");
    }}
  }}
  function addMessage(msg,type){{
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.textContent = msg;
    div.className = "message " + type;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
  }}
  document.querySelector("button").onclick = sendMessage;
  document.getElementById("userInput").onkeypress = function(e){{
    if(e.key==='Enter') sendMessage();
  }}
}}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_UI)

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_input = request.json.get("message", "")
    messages.append({"role":"user","content":user_input})

    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-(MAX_MESSAGES-1):]

    if not API_KEY:
        reply = "⚠️ API key not found. Add your key in Render Environment Variables."
    else:
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}",
                         "Content-Type": "application/json"},
                json={"model":"gpt-3.5-turbo","messages":messages},
                timeout=10
            )
            data = resp.json()
            if "error" in data:
                reply = f"OpenAI Error: {data['error']['message']}"
            else:
                reply = data["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Server error: {str(e)}"

    messages.append({"role":"assistant","content":reply})
    return jsonify({"reply":reply})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
