from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
import json
import os

app = Flask(__name__)
CORS(app)

# ✅ Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ✅ Set base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Load FAQ data
with open(os.path.join(BASE_DIR, "ai_aether_faq_updated.json"), "r", encoding="utf-8") as f:
    faq_data = json.load(f)
faq_context = "\n\n".join([f"Q: {q['question']}\nA: {q['answer']}" for q in faq_data])

# ✅ Chat route
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    print("Received user message:", user_msg)

    messages = [
       {
  "role": "system",
  "content":
    "You are the official chatbot of AI Aether. "
    "Answer user questions by referring to the following FAQ data. "
    "Rephrase answers clearly and professionally without changing their original meaning. "
    "Use new lines (\\n), bullet points, or emojis to make answers easy to read. "
    "Avoid long paragraphs; keep responses concise, helpful, and well-structured.\n\n" + faq_context
},

        {"role": "user", "content": user_msg}
    ]

    try:
        resp = client.chat.completions.create(
            model="llama3-70b-8192",  # ✅ Correct model name
            messages=messages,
            temperature=0.5,
            max_tokens=512,
            top_p=1,
        )
        print("Groq response raw:", resp)

        if not resp.choices:
            reply = "⚠️ No reply generated. Please try again."
        else:
            reply = resp.choices[0].message.content

    except Exception as e:
        print("Chat error:", e)
        reply = "❌ Groq API error: " + str(e)

    return jsonify({"reply": reply})

# ✅ Serve chatbot UI
@app.route("/chat_interface")
def chat_interface():
    return send_from_directory(BASE_DIR, "chat.html")

# ✅ Homepage for health check
@app.route("/", methods=["GET"])
def home():
    return "✅ AI Aether Chatbot Backend is running."

# ✅ Use Render-compatible run config
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
