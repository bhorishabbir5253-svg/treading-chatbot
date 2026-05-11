# chatbot.py
import os
import pickle
import numpy as np
import scipy.sparse as sp
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DB_FOLDER = "./trading_db"

# Load knowledge base
def load_knowledge_base():
    with open(f"{DB_FOLDER}/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    with open(f"{DB_FOLDER}/metadatas.pkl", "rb") as f:
        metadatas = pickle.load(f)
    with open(f"{DB_FOLDER}/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    tfidf_matrix = sp.load_npz(f"{DB_FOLDER}/tfidf_matrix.npz")
    return chunks, metadatas, vectorizer, tfidf_matrix

chunks, metadatas, vectorizer, tfidf_matrix = load_knowledge_base()
client = Groq(api_key=GROQ_API_KEY)

def get_relevant_chunks(question, k=3):
    query_vec = vectorizer.transform([question])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-k:][::-1]
    results = []
    for i in top_indices:
        results.append({
            "text": chunks[i],
            "source": metadatas[i]["source"]
        })
    return results

def load_trading_chatbot():
    print("🚀 Loading Trading Chatbot...")
    print("✅ Trading Chatbot Ready!")
    return ask_trading_question

def ask_trading_question(query_dict):
    question = query_dict["query"]

    # Get relevant chunks
    relevant = get_relevant_chunks(question, k=3)
    context = "\n\n".join([r["text"] for r in relevant])
    sources = list(set(r["source"] for r in relevant))

    prompt = f"""You are an expert Trading Assistant. Answer ONLY trading-related questions.
If the question is not about trading, say: "I only answer trading-related questions."

Be concise, clear and helpful. Use the context below from trading books to answer.

Context from Trading Books:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )

    answer = response.choices[0].message.content

    # Create fake doc objects for compatibility with app.py
    class Doc:
        def __init__(self, text, source):
            self.page_content = text
            self.metadata = {"source": source}

    docs = [Doc(r["text"], r["source"]) for r in relevant]

    return {
        "result": answer,
        "source_documents": docs
    }