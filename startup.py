# startup.py
import os
from ingest import build_vectorstore

DB_FOLDER = "./trading_db"
BOOKS_FOLDER = "./Books"

if not os.path.exists(f"{DB_FOLDER}/chunks.pkl"):
    if os.path.exists(BOOKS_FOLDER) and os.listdir(BOOKS_FOLDER):
        print("📚 Building knowledge base for first time...")
        build_vectorstore()
    else:
        print("⚠️ No books folder found — skipping")
else:
    print("✅ Knowledge base already exists!")