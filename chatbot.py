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

def load_knowledge_base():
    global chunks, metadatas, vectorizer
    with open(f"{DB_FOLDER}/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    with open(f"{DB_FOLDER}/metadatas.pkl", "rb") as f:
        metadatas = pickle.load(f)
    with open(f"{DB_FOLDER}/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    print(f"✅ Loaded {len(chunks)} chunks from knowledge base")

def get_relevant_chunks(question, k=3):
    query_vec = vectorizer.transform([question])
    doc_vecs = vectorizer.transform(chunks)
    similarities = cosine_similarity(query_vec, doc_vecs).flatten()
    top_indices = similarities.argsort()[-k:][::-1]
    return [
        {"text": chunks[i], "source": metadatas[i]}
        for i in top_indices
    ]

def load_trading_chatbot():
    print("🚀 Loading Trading Chatbot...")
    load_knowledge_base()
    print("✅ Trading Chatbot Ready!")
    return ask_trading_question

def ask_trading_question(query_dict):
    question = query_dict["query"]
    relevant = get_relevant_chunks(question, k=3)
    context = "\n\n".join([r["text"] for r in relevant])

    prompt = f"""You are an expert Trading Assistant specializing in stock markets, forex, technical analysis, candlestick patterns, trading strategies, and financial markets.

NOTE: The user may sometimes type "treading" but they always mean "trading" in financial markets. Always interpret "treading" as "trading".

IMPORTANT RULES:
- Answer ANY question related to trading, stocks, forex, markets, investing, candlesticks, indicators, strategies, risk management, or finance
- Only refuse if the question is completely unrelated to trading or finance (like cooking, sports, etc.)
- Always give a helpful answer using the context provided
- If context does not fully answer the question, use your trading knowledge to help

Context from Trading Books:
{context}

Question: {question}

Provide a clear and helpful trading answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=400
    )

    class Doc:
        def __init__(self, text, source):
            self.page_content = text
            self.metadata = {"source": source}

    return {
        "result": response.choices[0].message.content,
        "source_documents": [Doc(r["text"], r["source"]) for r in relevant]
    }