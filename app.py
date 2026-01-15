from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# ===== CONFIG =====
GROQ_API_KEY = os.getenv("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")  # <-- SAFE
MODEL = "llama3-70b-8192"

SYSTEM_PROMPT = """
You are ULTRA GPT.
You are extremely intelligent, clear, and helpful.
You understand typos and explain things simply.
"""

messages = []

LOGO_URL = "/static/logo.png"  # local, reliable

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ULTRA GPT</title>
<style>
body { margin:0; font-family:system-ui; background:#0b0f1a; color:#0ff; display:flex; }
#sidebar { width:220px; background:#050814; padding:10px; }
#chat { flex:1; display:flex; flex-direction:column; }
header { height:120px; display:flex; align-items:center; padding:15px;
background:linear-gradient(90deg,#00fff0,#7f00ff); color:black; font-size:28px; }
header img { height:70px; margin-right:10px; }
#messages { flex:1; padding:20px; overflow-y:auto; }
.msg { margin-bottom:14px; white-space:pre-wrap; }
.user { color:#00fff0; }
.bot { color:#ffe600; }
#inputBox { display:flex; padding:10px; background:#050814; }
input { flex:1; padding:12px; font-size:16px; background:#111; color:white; border:none; }
button { padding:12px; background:#7f00ff; color:white; border:none; cursor:pointer; }
</style>
</head>
<body>
<div id="sidebar">
<button onclick="reset()">+ New Chat</button>
</div>
<div id="chat">
<header>
<img src="{{ logo }}">
ULTRA GPT
</header>
<div id="messages"></div>
<div id="inputBox">
<input id="input" placeholder="Message ULTRA GPT...">
<button onclick="send()">Send</button>
</div>
</div>
<script>
function add(role,text){
 let d=document.createElement("div");
 d.className="msg "+role;
 d.textContent=(role==="user"?"You: ":"ULTRA GPT: ")+text;
 document.getElementById("messages").appendChild(d);
 d.scrollIntoView();
}
async function send(){
 let i=document.getElementById("input");
 if(!i.value) return;
 add("user",i.value);
 let r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:i.value})});
 let j=await r.json();
 add("bot",j.reply);
 i.value="";
}
async function reset(){
 await fetch("/reset",{method:"POST"});
 document.getElementById("messages").innerHTML="";
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, logo=LOGO_URL)

@app.route("/reset", methods=["POST"])
def reset():
    messages.clear()
    return jsonify(ok=True)

@app.route("/chat", methods=["POST"])
def chat():
    if not GROQ_API_KEY:
        return jsonify(reply="❌ GROQ_API_KEY not set in environment variables.")

    user_msg = request.json.get("message", "")
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": MODEL,
        "messages": [{"role":"system","content":SYSTEM_PROMPT}] + messages
    }

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        reply = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = "Server error: " + str(e)

    messages.append({"role": "assistant", "content": reply})
    return jsonify(reply=reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
