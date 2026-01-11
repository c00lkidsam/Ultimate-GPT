from flask import Flask, request, jsonify, render_template_string
import requests
import os  # Fix for NameError

app = Flask(__name__)

# ===== CONFIG =====
GROQ_API_KEY = "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"
MODEL = "llama3-70b-8192"

SYSTEM_PROMPT = """You are ULTRA GPT, a super-intelligent AI. 
- Understand typos and simplify or clarify anything.
- Provide answers like a well-researched assistant.
- Be witty, clear, and concise.
- Explain things like a teacher would, and structure replies well."""

# Chat history
messages = []

# UI Defaults
UI_SETTINGS = {
    "theme": "dark",
    "bg": "https://ih1.redbubble.net/image.5841016001.5391/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.u2.jpg",
    "font_size": 16
}

BG_GALLERY = [
    UI_SETTINGS["bg"],
    "https://i.pinimg.com/originals/1e/7b/99/1e7b99f7a1f3dbec.jpg",
    "https://i.pinimg.com/originals/d3/47/88/d3478894e43b9a7a.jpg"
]

LOGO_URL = "https://i.ibb.co/7gS6Xw7/forsaken1x.png"

# ===== HTML/UI =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ULTRA GPT</title>
<style>
body { margin:0; font-family:system-ui; display:flex; transition: background 0.3s; background:{bg} no-repeat center/cover; color:{text_color}; }
#sidebar { width:250px; background:{sidebar_bg}; padding:10px; }
#newChat,#openSettings{width:100%;padding:12px;background:#111; border:1px solid #19c37d; color:#19c37d; font-weight:bold; cursor:pointer; font-size:15px; margin-bottom:6px; text-shadow:0 0 6px #19c37d;}
#newChat:hover,#openSettings:hover{background:#19c37d; color:#111; transition:0.3s;}
#chat{flex:1; display:flex; flex-direction:column;}
header{height:140px; display:flex; align-items:center; padding:15px; font-size:28px; font-weight:bold; text-shadow:0 0 10px #00fff0; background:url('{bg}') center/cover no-repeat;}
header img{height:80px; margin-right:10px; filter: drop-shadow(0 0 10px #00fff0);}
#messages{flex:1; padding:20px; overflow-y:auto; font-size:{font_size}px;}
.msg{margin-bottom:16px; white-space:pre-wrap;}
.user{color:#0ff;}
.bot{color:#ff0; text-shadow:0 0 8px #ff0;}
#inputBox{display:flex; padding:12px; background:#111; border-top:1px solid #19c37d;}
input{flex:1; padding:12px; font-size:16px; border:none; outline:none; background:#222; color:#fff; border-radius:4px; box-shadow:0 0 8px #0ff inset;}
button{background:#19c37d; border:none; padding:12px; cursor:pointer; border-radius:4px; box-shadow:0 0 12px #19c37d;}
button:hover{background:#0ff; color:#111; transition:0.3s;}
#settingsPanel{display:none; padding:10px; background:#111; color:#0ff;}
#settingsPanel label{display:block; margin-top:6px;}
#bgGallery img{width:60px; margin:4px; cursor:pointer; border:2px solid transparent; border-radius:4px; transition:0.2s;}
#bgGallery img.selected{border-color:#19c37d; box-shadow:0 0 12px #19c37d;}
</style>
</head>
<body>
<div id="sidebar">
  <button id="newChat">+ New Chat</button>
  <button id="openSettings">⚡ Settings</button>
  <div id="settingsPanel">
    <label>Theme:
      <select id="themeSelect">
        <option value="dark">Dark</option>
        <option value="light">Light</option>
      </select>
    </label>
    <label>Font Size:
      <input type="number" id="fontSize" min="12" max="28" value="{font_size}">
    </label>
    <label>Background:</label>
    <div id="bgGallery">{bg_imgs}</div>
    <label>Edit SYSTEM_PROMPT:</label>
    <textarea id="sysPrompt" rows="5" style="width:100%">{system_prompt}</textarea>
    <button id="saveSettings">Save Settings</button>
  </div>
</div>
<div id="chat">
  <header><img src="{logo}" alt="ULTRA GPT Logo"/>ULTRA GPT</header>
  <div id="messages"></div>
  <div id="inputBox">
    <input id="input" placeholder="Message ULTRA GPT..."/>
    <button onclick="send()">Send</button>
  </div>
</div>
<script>
function add(role,text){const d=document.createElement("div"); d.className="msg "+role; d.textContent=(role==="user"?"You: ":"ULTRA GPT: ")+text; document.getElementById("messages").appendChild(d); d.scrollIntoView();}
async function send(){const i=document.getElementById("input"); if(!i.value) return; add("user",i.value); const r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:i.value})}); const j=await r.json(); add("bot",j.reply); i.value="";}
document.getElementById("newChat").onclick=async()=>{await fetch("/reset",{method:"POST"}); document.getElementById("messages").innerHTML="";};
document.getElementById("openSettings").onclick=()=>{const p=document.getElementById("settingsPanel"); p.style.display=(p.style.display==="none"?"block":"none");};
document.getElementById("saveSettings").onclick=async()=>{const theme=document.getElementById("themeSelect").value; const font=parseInt(document.getElementById("fontSize").value); const bg=document.querySelector("#bgGallery img.selected")?.src||""; const sys=document.getElementById("sysPrompt").value; await fetch("/settings",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({theme,font,bg,sys})}); location.reload();};
document.querySelectorAll("#bgGallery img").forEach(img=>{img.onclick=()=>{document.querySelectorAll("#bgGallery img").forEach(i=>i.classList.remove("selected")); img.classList.add("selected");};});
</script>
</body>
</html>
"""

bg_imgs_html = "".join([f'<img src="{b}"/>' for b in BG_GALLERY])

# ===== ROUTES =====
@app.route("/")
def home():
    theme = UI_SETTINGS["theme"]
    font_size = UI_SETTINGS["font_size"]
    bg = UI_SETTINGS["bg"]
    text_color = "#FFF" if theme=="dark" else "#000"
    sidebar_bg = "#202123" if theme=="dark" else "#EEE"
    return render_template_string(
        HTML,
        bg=bg,
        text_color=text_color,
        sidebar_bg=sidebar_bg,
        font_size=font_size,
        system_prompt=SYSTEM_PROMPT,
        bg_imgs=bg_imgs_html,
        logo=LOGO_URL
    )

@app.route("/reset", methods=["POST"])
def reset():
    global messages
    messages.clear()
    return jsonify({"ok": True})

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_msg = request.json.get("message","")
    messages.append(user_msg)

    # Groq API call
    payload = {
        "model": MODEL,
        "input": SYSTEM_PROMPT + "\n" + "\n".join(messages),
        "max_output_tokens": 500
    }

    try:
        res = requests.post(
            "https://api.groq.com/v1/llm/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        data = res.json()
        reply = data.get("content","No reply from server")
    except Exception as e:
        reply = "Server error: " + str(e)

    messages.append(reply)
    return jsonify({"reply": reply})

@app.route("/settings", methods=["POST"])
def settings():
    global UI_SETTINGS, SYSTEM_PROMPT, messages
    d = request.json
    UI_SETTINGS["theme"] = d.get("theme","dark")
    UI_SETTINGS["font_size"] = d.get("font",16)
    if d.get("bg"): UI_SETTINGS["bg"] = d["bg"]
    SYSTEM_PROMPT = d.get("sys",SYSTEM_PROMPT)
    messages.clear()
    return jsonify({"ok": True})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
