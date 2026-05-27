# app.py
import os
from flask import Flask, request, jsonify, render_template_string
from startup import *
from chatbot import load_trading_chatbot, clear_history

app = Flask(__name__)
qa_chain = load_trading_chatbot()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Chatbot</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 50%, #0a0f1e 100%);
    min-height: 100vh;
    color: #e0e0e0;
    display: flex;
    flex-direction: column;
  }

  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
      radial-gradient(ellipse at 20% 20%, rgba(34, 197, 94, 0.05) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }

  header {
    background: rgba(22, 27, 34, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(34, 197, 94, 0.2);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .logo {
    width: 42px;
    height: 42px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
  }

  .header-title h1 { font-size: 1.2rem; font-weight: 700; color: #fff; letter-spacing: -0.3px; }
  .header-title p { font-size: 0.72rem; color: #6b7280; margin-top: 1px; }

  .header-right { display: flex; align-items: center; gap: 10px; }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 7px;
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    color: #22c55e;
    font-weight: 500;
  }

  .status-dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }

  .clear-btn {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
  }

  .clear-btn:hover { background: rgba(239, 68, 68, 0.2); }

  /* Sidebar toggle button */
  .sidebar-toggle {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #3b82f6;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.75rem;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
  }

  .sidebar-toggle:hover { background: rgba(59, 130, 246, 0.2); }

  /* Layout with sidebar */
  .layout {
    display: flex;
    flex: 1;
    position: relative;
    z-index: 1;
  }

  /* Sidebar */
  .sidebar {
    width: 300px;
    background: rgba(22, 27, 34, 0.95);
    border-right: 1px solid rgba(34, 197, 94, 0.1);
    padding: 20px;
    overflow-y: auto;
    transition: all 0.3s ease;
    flex-shrink: 0;
  }

  .sidebar.hidden { display: none; }

  .sidebar h3 {
    font-size: 0.85rem;
    font-weight: 600;
    color: #22c55e;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(34, 197, 94, 0.2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .term-item {
    margin-bottom: 14px;
    padding: 10px 12px;
    background: rgba(15, 17, 23, 0.6);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .term-item:hover {
    border-color: rgba(34, 197, 94, 0.3);
    background: rgba(34, 197, 94, 0.05);
  }

  .term-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #22c55e;
    margin-bottom: 4px;
  }

  .term-def {
    font-size: 0.72rem;
    color: #6b7280;
    line-height: 1.5;
  }

  /* Main content */
  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    max-width: 900px;
    width: 100%;
    margin: 0 auto;
    padding: 24px 20px;
  }

  .welcome { text-align: center; padding: 40px 20px 30px; }

  .welcome-icon {
    font-size: 3.5rem;
    margin-bottom: 16px;
    display: block;
    filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.4));
  }

  .welcome h2 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #22c55e, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .welcome p { color: #6b7280; font-size: 0.9rem; max-width: 500px; margin: 0 auto; line-height: 1.6; }

  .quick-questions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 20px 0; }

  .quick-btn {
    background: rgba(22, 27, 34, 0.8);
    border: 1px solid rgba(34, 197, 94, 0.2);
    color: #9ca3af;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
  }

  .quick-btn:hover { border-color: #22c55e; color: #22c55e; background: rgba(34, 197, 94, 0.08); transform: translateY(-1px); }

  .stats-bar { display: flex; gap: 16px; justify-content: center; margin: 16px 0; flex-wrap: wrap; }

  .stat {
    background: rgba(22, 27, 34, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 8px 16px;
    text-align: center;
    font-size: 0.72rem;
  }

  .stat-value { color: #22c55e; font-weight: 700; font-size: 0.95rem; display: block; }
  .stat-label { color: #4b5563; margin-top: 2px; }

  #chat-box { flex: 1; display: flex; flex-direction: column; gap: 20px; padding: 10px 0; min-height: 200px; }

  .message { display: flex; gap: 12px; animation: fadeIn 0.3s ease; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .message.user { flex-direction: row-reverse; }

  .avatar {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
  }

  .avatar.bot { background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 0 15px rgba(34, 197, 94, 0.3); }
  .avatar.user { background: linear-gradient(135deg, #3b82f6, #2563eb); box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); }

  .bubble { max-width: 75%; padding: 14px 18px; border-radius: 16px; line-height: 1.7; font-size: 0.9rem; }

  .bubble.bot {
    background: rgba(22, 27, 34, 0.9);
    border: 1px solid rgba(34, 197, 94, 0.15);
    border-bottom-left-radius: 4px;
    color: #e0e0e0;
  }

  .bubble.user {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.08));
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-bottom-right-radius: 4px;
    color: #e0e0e0;
  }

  .sources {
    margin-top: 10px; padding-top: 8px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.72rem; color: #4b5563;
    display: flex; align-items: center; gap: 5px;
  }

  /* Copy button */
  .copy-btn {
    background: none;
    border: 1px solid rgba(255,255,255,0.08);
    color: #4b5563;
    font-size: 0.7rem;
    cursor: pointer;
    padding: 4px 10px;
    border-radius: 6px;
    margin-top: 8px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
  }

  .copy-btn:hover { border-color: #22c55e; color: #22c55e; }

  /* Typing indicator */
  .typing-bubble {
    background: rgba(22, 27, 34, 0.9);
    border: 1px solid rgba(34, 197, 94, 0.15);
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    padding: 14px 18px;
    display: flex; align-items: center; gap: 5px;
  }

  .typing-dot { width: 7px; height: 7px; background: #22c55e; border-radius: 50%; animation: bounce 1.2s infinite; }
  .typing-dot:nth-child(2) { animation-delay: 0.2s; }
  .typing-dot:nth-child(3) { animation-delay: 0.4s; }

  @keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
  }

  /* Input area */
  .input-wrapper {
    background: rgba(22, 27, 34, 0.95);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(34, 197, 94, 0.1);
    padding: 20px;
    position: sticky;
    bottom: 0;
    z-index: 100;
  }

  .input-container { max-width: 900px; margin: 0 auto; display: flex; gap: 12px; align-items: flex-end; }

  .input-box {
    flex: 1;
    background: rgba(15, 17, 23, 0.8);
    border: 1px solid rgba(34, 197, 94, 0.2);
    border-radius: 14px;
    padding: 14px 18px;
    color: #e0e0e0;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
    outline: none;
    resize: none;
    min-height: 52px;
    max-height: 140px;
    transition: border-color 0.2s;
    line-height: 1.5;
  }

  .input-box:focus { border-color: #22c55e; box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.08); }
  .input-box::placeholder { color: #374151; }

  .send-btn {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    border: none; border-radius: 14px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3); flex-shrink: 0;
  }

  .send-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4); }
  .send-btn:active { transform: translateY(0); }
  .send-btn:disabled { background: #1f2937; box-shadow: none; cursor: not-allowed; transform: none; }

  /* Voice button */
  .voice-btn {
    width: 52px; height: 52px;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.4);
    border-radius: 14px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; transition: all 0.2s ease; flex-shrink: 0;
  }

  .voice-btn:hover { background: rgba(59, 130, 246, 0.25); transform: translateY(-2px); }
  .voice-btn.listening { background: rgba(239, 68, 68, 0.2); border-color: #ef4444; animation: voicePulse 1s infinite; }

  @keyframes voicePulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
    50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
  }

  .input-hint { text-align: center; font-size: 0.7rem; color: #374151; margin-top: 8px; }

  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(34, 197, 94, 0.2); border-radius: 2px; }

  @media (max-width: 768px) {
    .sidebar { display: none !important; }
    header { padding: 12px 16px; }
    .main { padding: 16px 12px; }
    .welcome h2 { font-size: 1.4rem; }
    .bubble { max-width: 90%; }
    .stats-bar { gap: 8px; }
  }
</style>
</head>
<body>

<header>
  <div class="header-left">
    <div class="logo">📈</div>
    <div class="header-title">
      <h1>Trading Chatbot</h1>
      <p>Powered by your Trading Books • AI by Groq</p>
    </div>
  </div>
  <div class="header-right">
    <button class="sidebar-toggle" onclick="toggleSidebar()">📖 Terms</button>
    <button class="clear-btn" onclick="clearChat()">🗑️ Clear Chat</button>
    <div class="status-badge">
      <div class="status-dot"></div>
      Online
    </div>
  </div>
</header>

<div class="layout">

  <!-- Trading Terms Sidebar -->
  <div class="sidebar hidden" id="sidebar">
    <h3>📚 Trading Terms</h3>

    <div class="term-item" onclick="setQ('What is RSI indicator?')">
      <div class="term-name">RSI — Relative Strength Index</div>
      <div class="term-def">Momentum oscillator measuring speed and change of price movements. Range: 0-100. Above 70 = overbought, below 30 = oversold.</div>
    </div>

    <div class="term-item" onclick="setQ('Explain MACD indicator')">
      <div class="term-name">MACD</div>
      <div class="term-def">Moving Average Convergence Divergence. Shows relationship between two moving averages of price.</div>
    </div>

    <div class="term-item" onclick="setQ('What is a bullish engulfing pattern?')">
      <div class="term-name">Bullish Engulfing</div>
      <div class="term-def">A candlestick pattern where a large green candle completely engulfs the previous red candle. Strong bullish reversal signal.</div>
    </div>

    <div class="term-item" onclick="setQ('What is support and resistance?')">
      <div class="term-name">Support & Resistance</div>
      <div class="term-def">Price levels where buying (support) or selling (resistance) pressure is strong enough to halt price movement.</div>
    </div>

    <div class="term-item" onclick="setQ('What is a stop loss?')">
      <div class="term-name">Stop Loss</div>
      <div class="term-def">An order to sell a security when it reaches a certain price to limit losses on a trade.</div>
    </div>

    <div class="term-item" onclick="setQ('What is moving average?')">
      <div class="term-name">Moving Average (MA)</div>
      <div class="term-def">Average price over a specific period. SMA = Simple, EMA = Exponential. Used to identify trend direction.</div>
    </div>

    <div class="term-item" onclick="setQ('What is Bollinger Bands?')">
      <div class="term-name">Bollinger Bands</div>
      <div class="term-def">Volatility bands placed above and below a moving average. Price touching upper band = overbought, lower band = oversold.</div>
    </div>

    <div class="term-item" onclick="setQ('What is risk reward ratio?')">
      <div class="term-name">Risk/Reward Ratio</div>
      <div class="term-def">Compares potential profit to potential loss. A 1:3 ratio means risking $1 to make $3. Minimum recommended is 1:2.</div>
    </div>

    <div class="term-item" onclick="setQ('What is a doji candlestick?')">
      <div class="term-name">Doji Candlestick</div>
      <div class="term-def">Candle where open and close are almost equal. Indicates market indecision and potential reversal.</div>
    </div>

    <div class="term-item" onclick="setQ('What is breakout trading?')">
      <div class="term-name">Breakout</div>
      <div class="term-def">When price moves beyond a support or resistance level with increased volume. Signals potential strong move.</div>
    </div>

    <div class="term-item" onclick="setQ('What is position sizing?')">
      <div class="term-name">Position Sizing</div>
      <div class="term-def">Determining how much of your capital to risk on a single trade. Key part of risk management.</div>
    </div>

    <div class="term-item" onclick="setQ('What is trend analysis?')">
      <div class="term-name">Trend</div>
      <div class="term-def">General direction of market movement. Uptrend = higher highs and higher lows. Downtrend = lower highs and lower lows.</div>
    </div>

    <div class="term-item" onclick="setQ('What is fibonacci retracement?')">
      <div class="term-name">Fibonacci Retracement</div>
      <div class="term-def">Tool using Fibonacci ratios (23.6%, 38.2%, 61.8%) to identify potential support/resistance levels.</div>
    </div>

    <div class="term-item" onclick="setQ('What is volume in trading?')">
      <div class="term-name">Volume</div>
      <div class="term-def">Number of shares/contracts traded in a period. High volume confirms price movements and trends.</div>
    </div>
  </div>

  <!-- Main Chat Area -->
  <div class="main">
    <div class="welcome" id="welcome-section">
      <span class="welcome-icon">📊</span>
      <h2>Your Personal Trading Assistant</h2>
      <p>Ask me anything about trading — from candlestick patterns to risk management strategies. Powered by expert trading books.</p>

      <div class="stats-bar">
        <div class="stat">
          <span class="stat-value">7</span>
          <span class="stat-label">Trading Books</span>
        </div>
        <div class="stat">
          <span class="stat-value">⚡ Fast</span>
          <span class="stat-label">AI Responses</span>
        </div>
        <div class="stat">
          <span class="stat-value">24/7</span>
          <span class="stat-label">Available</span>
        </div>
      </div>

      <div class="quick-questions">
        <button class="quick-btn" onclick="setQ('What is technical analysis?')">📊 Technical Analysis</button>
        <button class="quick-btn" onclick="setQ('Explain candlestick patterns')">🕯️ Candlestick Patterns</button>
        <button class="quick-btn" onclick="setQ('What is RSI indicator?')">📈 RSI Indicator</button>
        <button class="quick-btn" onclick="setQ('How to manage risk in trading?')">🛡️ Risk Management</button>
        <button class="quick-btn" onclick="setQ('What is support and resistance?')">📉 Support & Resistance</button>
        <button class="quick-btn" onclick="setQ('Explain MACD indicator')">⚡ MACD</button>
        <button class="quick-btn" onclick="setQ('What is a bullish engulfing pattern?')">🕯️ Bullish Engulfing</button>
        <button class="quick-btn" onclick="setQ('How to start trading as a beginner?')">🚀 Beginner Guide</button>
        <button class="quick-btn" onclick="setQ('What is moving average?')">〰️ Moving Average</button>
        <button class="quick-btn" onclick="setQ('Explain moving average crossover strategy')">📉 MA Crossover</button>
      </div>
    </div>

    <div id="chat-box"></div>
  </div>

</div>

<div class="input-wrapper">
  <div class="input-container">
    <button class="voice-btn" id="voice-btn" onclick="startVoice()" title="Voice Input">🎤</button>
    <textarea
      id="user-input"
      class="input-box"
      placeholder="Ask anything about trading... or click 🎤 to speak"
      rows="1"
      onkeydown="handleKey(event)"
      oninput="autoResize(this)"
    ></textarea>
    <button class="send-btn" id="send-btn" onclick="sendMsg()">➤</button>
  </div>
  <div class="input-hint">Press Enter to send • Shift+Enter for new line • 🎤 for voice input</div>
</div>

<script>
// ===== SIDEBAR =====
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('hidden');
}

// ===== VOICE INPUT =====
let recognition = null;
let isListening = false;

function startVoice() {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert('Voice input is not supported in your browser. Please use Chrome.');
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const voiceBtn = document.getElementById('voice-btn');

  if (isListening) {
    recognition.stop();
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isListening = true;
    voiceBtn.classList.add('listening');
    voiceBtn.textContent = '🔴';
  };

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    document.getElementById('user-input').value = transcript;
    autoResize(document.getElementById('user-input'));
  };

  recognition.onend = () => {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceBtn.textContent = '🎤';
  };

  recognition.onerror = () => {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceBtn.textContent = '🎤';
  };

  recognition.start();
}

// ===== CLEAR CHAT =====
async function clearChat() {
  document.getElementById('chat-box').innerHTML = '';
  document.getElementById('welcome-section').style.display = 'block';
  try {
    await fetch('/clear', { method: 'POST' });
  } catch(e) {}
}

// ===== INPUT HELPERS =====
function setQ(text) {
  document.getElementById('user-input').value = text;
  document.getElementById('user-input').focus();
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMsg();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

// ===== ADD MESSAGE =====
function addMessage(text, isUser, sources) {
  const chatBox = document.getElementById('chat-box');

  const msg = document.createElement('div');
  msg.className = `message ${isUser ? 'user' : 'bot'}`;

  const avatar = document.createElement('div');
  avatar.className = `avatar ${isUser ? 'user' : 'bot'}`;
  avatar.textContent = isUser ? '👤' : '📈';

  const bubble = document.createElement('div');
  bubble.className = `bubble ${isUser ? 'user' : 'bot'}`;
  bubble.innerHTML = escapeHtml(text).replace(/\\n/g, '<br>');

  // Copy button for bot messages
  if (!isUser) {
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.innerHTML = '📋 Copy';
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.innerHTML = '✅ Copied!';
        setTimeout(() => { copyBtn.innerHTML = '📋 Copy'; }, 2000);
      });
    };
    bubble.appendChild(copyBtn);
  }

  // Sources
  if (!isUser && sources && sources.length > 0) {
    const src = document.createElement('div');
    src.className = 'sources';
    src.innerHTML = `📚 Sources: ${sources.map(s => escapeHtml(s)).join(', ')}`;
    bubble.appendChild(src);
  }

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
  window.scrollTo(0, document.body.scrollHeight);
}

// ===== TYPING INDICATOR =====
function showTyping() {
  const chatBox = document.getElementById('chat-box');
  const msg = document.createElement('div');
  msg.className = 'message bot';
  msg.id = 'typing-indicator';

  const avatar = document.createElement('div');
  avatar.className = 'avatar bot';
  avatar.textContent = '📈';

  const bubble = document.createElement('div');
  bubble.className = 'typing-bubble';
  bubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
  const t = document.getElementById('typing-indicator');
  if (t) t.remove();
}

// ===== SEND MESSAGE =====
async function sendMsg() {
  const input = document.getElementById('user-input');
  const question = input.value.trim();
  if (!question) return;

  document.getElementById('welcome-section').style.display = 'none';

  addMessage(question, true);
  input.value = '';
  input.style.height = 'auto';

  const btn = document.getElementById('send-btn');
  btn.disabled = true;
  showTyping();

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await response.json();
    hideTyping();
    addMessage(data.answer, false, data.sources);
  } catch (err) {
    hideTyping();
    addMessage('❌ Error connecting. Please try again.', false, []);
  }

  btn.disabled = false;
  input.focus();
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
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

@app.route("/clear", methods=["POST"])
def clear():
    clear_history()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"\n✅ Trading Chatbot running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)