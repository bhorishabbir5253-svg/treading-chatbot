# chatbot.py
import os
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DB_FOLDER = "./trading_db"

client = Groq(api_key=GROQ_API_KEY)

chunks = None
metadatas = None
vectorizer = None

# Chat memory storage
conversation_history = []

def load_knowledge_base():
    global chunks, metadatas, vectorizer
    with open(f"{DB_FOLDER}/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    with open(f"{DB_FOLDER}/metadatas.pkl", "rb") as f:
        metadatas = pickle.load(f)
    with open(f"{DB_FOLDER}/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    print(f"✅ Loaded {len(chunks)} chunks from knowledge base")

def get_relevant_chunks(question, k=6):
    query_vec = vectorizer.transform([question])
    doc_vecs = vectorizer.transform(chunks)
    similarities = cosine_similarity(query_vec, doc_vecs).flatten()
    top_indices = similarities.argsort()[-k:][::-1]
    return [
        {"text": chunks[i], "source": metadatas[i]}
        for i in top_indices
    ]

def get_conversation_history():
    # Return last 4 messages for context
    history_text = ""
    if conversation_history:
        for h in conversation_history[-4:]:
            history_text += f"User: {h['user']}\nAssistant: {h['bot']}\n\n"
    return history_text

def load_trading_chatbot():
    print("🚀 Loading Trading Chatbot...")
    load_knowledge_base()
    print("✅ Trading Chatbot Ready!")
    return ask_trading_question

def ask_trading_question(query_dict):
    global conversation_history

    question = query_dict["query"]
    relevant = get_relevant_chunks(question, k=6)
    context = "\n\n".join([r["text"] for r in relevant])

    # Get conversation history
    history_text = get_conversation_history()

    prompt = f"""You are an expert Trading Assistant with deep knowledge in all these topics:

📊 TECHNICAL ANALYSIS
- Chart patterns (Head & Shoulders, Double Top/Bottom, Triangles, Flags)
- Trend analysis, trendlines, channels
- Volume analysis and price action

🕯️ CANDLESTICK PATTERNS
- Bullish patterns (Hammer, Bullish Engulfing, Morning Star, Doji)
- Bearish patterns (Shooting Star, Bearish Engulfing, Evening Star)
- Neutral patterns and their significance

📈 TRADING STRATEGIES
- Day trading, Swing trading, Position trading, Scalping
- Breakout strategies, Trend following, Mean reversion
- Entry and exit strategies

⚡ TECHNICAL INDICATORS
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands, Moving Averages (SMA, EMA)
- Stochastic, ATR, Fibonacci retracements

🛡️ RISK MANAGEMENT
- Stop loss placement and position sizing
- Risk/Reward ratio and portfolio management
- Drawdown management and capital preservation

💹 MARKETS
- Stock market, Forex, Commodities, Crypto
- Market structure, trends, and cycles
- Fundamental vs Technical analysis

🧠 TRADING PSYCHOLOGY
- Discipline, patience, and emotional control
- Overcoming fear and greed
- Building a trading mindset

NOTE: The user may sometimes type "treading" but they always mean "trading" in financial markets. Always interpret "treading" as "trading".

IMPORTANT RULES:
- Answer ANY question related to trading, stocks, forex, markets, investing, candlesticks, indicators, strategies, risk management, or finance
- Only refuse if the question is completely unrelated to trading or finance (like cooking, sports, etc.)
- Always give a helpful, detailed answer using the context provided
- If context does not fully answer the question, use your expert trading knowledge
- Remember the conversation history and give connected answers
- Use examples where possible to explain concepts clearly

Previous Conversation:
{history_text}

Context from Trading Books:
{context}

Current Question: {question}

Provide a clear, detailed and helpful trading answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024
    )

    answer = response.choices[0].message.content

    # Save to conversation history
    conversation_history.append({
        "user": question,
        "bot": answer
    })

    # Keep only last 10 conversations to save memory
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    class Doc:
        def __init__(self, text, source):
            self.page_content = text
            self.metadata = {"source": source}

    return {
        "result": answer,
        "source_documents": [Doc(r["text"], r["source"]) for r in relevant]
    }

def clear_history():
    global conversation_history
    conversation_history = []
    print("🗑️ Conversation history cleared!")