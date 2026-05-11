# chatbot.py
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

# Load .env file
load_dotenv()

# Get API key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

DB_FOLDER = "./trading_db"

# Load embeddings and vectorstore once
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=DB_FOLDER,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Groq client
client = Groq(api_key=GROQ_API_KEY)

def load_trading_chatbot():
    print("🚀 Loading Trading Chatbot...")
    print("✅ Trading Chatbot Ready!")
    return ask_trading_question

def ask_trading_question(query_dict):
    question = query_dict["query"]

    # Get relevant chunks from your books
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Send to Groq
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

    return {
        "result": answer,
        "source_documents": docs
    }