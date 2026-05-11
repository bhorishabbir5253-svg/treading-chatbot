import os
from flask import Flask, request, jsonify, render_template_string
from startup import *          # builds DB if not exists
from chatbot import load_trading_chatbot

app = Flask(__name__)
qa_chain = load_trading_chatbot()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Chatbot</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; height: 100vh; display: flex; flex-direction: column; }
  header { background: #161b22; border-bottom: 1px solid #22c55e33; padding: 16px 24px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 1.4rem; color: #22c55e; }
  header span { font-size: 0.85rem; color: #6b7280; }
  #chat-box { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
  .msg { max-width: 75%; padding: 12px 16px; border-radius: 12px; line-height: 1.6; font-size: 0.95rem; }
  .user-msg { background: #22c55e22; border: 1px solid #22c55e44; align-self: flex-end; border-bottom-right-radius: 4px; }
  .bot-msg { background: #161b22; border: 1px solid #30363d; align-self: flex-start; border-bottom-left-radius: 4px; }
  .bot-msg .sources { margin-top: 8px; font-size: 0.78rem; color: #6b7280; border-top: 1px solid #30363d; padding-top: 6px; }
  .typing { color: #22c55e; font-style: italic; font-size: 0.85rem; }
  #input-area { background: #161b22; border-top: 1px solid #30363d; padding: 16px 24px; display: flex; gap: 12px; }
  #user-input { flex: 1; background: #0f1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px; color: #e0e0e0; font-size: 0.95rem; outline: none; }
  #user-input:focus { border-color: #22c55e; }
  #send-btn { background: #22c55e; color: #000; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; cursor: pointer; font-size: 0.95rem; }
  #send-btn:hover { background: #16a34a; }
  #send-btn:disabled { background: #374151; color: #6b7280; cursor: not-allowed; }
  .examples { padding: 0 24px 16px; display: flex; flex-wrap: wrap; gap: 8px; }
  .ex-btn { background: #161b22; border: 1px solid #30363d; color: #9ca3af; border-radius: 20px; padding: 6px 14px; font-size: 0.8rem; cursor: pointer; }
  .ex-btn:hover { border-color: #22c55e; color: #22c55e; }
</style>
</head>
<body>

<header>
  <span style="font-size:1.8rem">📈</span>
  <div>
    <h1>Trading Chatbot</h1>
    <span>Powered by your Trading Books</span>
  </div>
</header>

<div id="chat-box">
  <div class="msg bot-msg">👋 Hello! I'm your Trading Assistant. Ask me anything about trading — candlestick patterns, indicators, strategies, risk management, and more!</div>
</div>

<div class="examples" id="examples">
  <button class="ex-btn" onclick="setQ('What is a bullish engulfing pattern?')">Bullish Engulfing</button>
  <button class="ex-btn" onclick="setQ('Explain RSI indicator')">RSI Indicator</button>
  <button class="ex-btn" onclick="setQ('What is support and resistance?')">Support & Resistance</button>
  <button class="ex-btn" onclick="setQ('How to manage risk in trading?')">Risk Management</button>
  <button class="ex-btn" onclick="setQ('What is MACD?')">MACD</button>
  <button class="ex-btn" onclick="setQ('Explain moving average crossover strategy')">MA Crossover</button>
</div>

<div id="input-area">
  <input id="user-input" type="text" placeholder="Ask about trading..." onkeydown="if(event.key==='Enter') sendMsg()" />
  <button id="send-btn" onclick="sendMsg()">Send ➤</button>
</div>

<script>
function setQ(text) {
  document.getElementById('user-input').value = text;
  document.getElementById('user-input').focus();
}

async function sendMsg() {
  const input = document.getElementById('user-input');
  const question = input.value.trim();
  if (!question) return;

  const chatBox = document.getElementById('chat-box');
  const btn = document.getElementById('send-btn');

  // Hide examples after first message
  document.getElementById('examples').style.display = 'none';

  // Show user message
  chatBox.innerHTML += `<div class="msg user-msg">${escapeHtml(question)}</div>`;
  input.value = '';
  btn.disabled = true;

  // Show typing indicator
  const typingId = 'typing-' + Date.now();
  chatBox.innerHTML += `<div class="msg bot-msg typing" id="${typingId}">⏳ Searching your trading books...</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();

    // Remove typing indicator
    document.getElementById(typingId).remove();

    let html = `<div class="msg bot-msg">${escapeHtml(data.answer).replace(/\\n/g, '<br>')}`;
    if (data.sources && data.sources.length > 0) {
      html += `<div class="sources">📚 Sources: ${data.sources.join(', ')}</div>`;
    }
    html += `</div>`;
    chatBox.innerHTML += html;

  } catch (err) {
    document.getElementById(typingId).remove();
    chatBox.innerHTML += `<div class="msg bot-msg" style="color:#ef4444">❌ Error getting response. Make sure Ollama is running.</div>`;
  }

  btn.disabled = false;
  chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please ask a question.", "sources": []})

    try:
        result = qa_chain({"query": question})
        answer = result["result"]
        sources = list(set(
            doc.metadata.get("source", "")
            for doc in result.get("source_documents", [])
            if doc.metadata.get("source")
        ))
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}", "sources": []})

   # Change this at the bottom of app.py
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✅ Trading Chatbot running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)