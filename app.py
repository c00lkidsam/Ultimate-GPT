from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# ===== CONFIG =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "YOUR_GROQ_KEY_HERE"
MODEL = "llama3-70b-8192"

SYSTEM_PROMPT = """
You are ULTRA GPT.
You understand typos, simplify answers, explain clearly,
and respond intelligently like ChatGPT mixed with Gronk-level reasoning.
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Default UI settings
UI_SETTINGS = {
    "theme": "dark",
    "bg": "https://ih1.redbubble.net/image.5841016001.5391/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.u2.jpg",
    "font_size": 16
}

BG_GALLERY = [
    "https://ih1.redbubble.net/image.5841016001.5391/bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.u2.jpg",
    "https://i.pinimg.com/originals/1e/7b/99/1e7b99f7a1f3dbec.jpg",
    "https://i.pinimg.com/originals/d3/47/88/d3478894e43b9a7a.jpg"
]

LOGO_URL = "https://i.ibb.co/7gS6Xw7/forsaken1x.png"

# ===== HTML/UI =====
HTML = """ (Keep your HTML same as previous version, replace {bg}, {font_size}, {logo} etc.) """

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
    messages = [{"role":"system","content":SYSTEM_PROMPT}]
    return jsonify({"ok": True})

@app.route("/chat", methods=["POST"])
def chat():
    global messages
    user_msg = request.json.get("message","")
    messages.append({"role":"user","content":user_msg})

    try:
        # === Updated Groq endpoint ===
        res = requests.post(
            "https://api.groq.com/v1/llm/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "input": "\n".join([m["content"] for m in messages]),
                "max_output_tokens": 500
            },
            timeout=20
        )
        data = res.json()
        # Groq responses usually return 'content'
        reply = data.get("content","No reply from server")
    except Exception as e:
        reply = "Server error: " + str(e)

    messages.append({"role":"assistant","content":reply})
    return jsonify({"reply": reply})

@app.route("/settings", methods=["POST"])
def settings():
    global UI_SETTINGS, SYSTEM_PROMPT
    d = request.json
    UI_SETTINGS["theme"] = d.get("theme","dark")
    UI_SETTINGS["font_size"] = d.get("font",16)
    if d.get("bg"): UI_SETTINGS["bg"] = d["bg"]
    SYSTEM_PROMPT = d.get("sys", SYSTEM_PROMPT)
    messages.clear()
    messages.append({"role":"system","content":SYSTEM_PROMPT})
    return jsonify({"ok": True})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
