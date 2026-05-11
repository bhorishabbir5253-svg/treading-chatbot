# startup.py
import os
from ingest import build_vectorstore

DB_FOLDER = "./trading_db"
BOOKS_FOLDER = "./Books"

# Build knowledge base on first startup if it doesn't exist
if not os.path.exists(DB_FOLDER) or not os.listdir(DB_FOLDER):
    if os.path.exists(BOOKS_FOLDER) and os.listdir(BOOKS_FOLDER):
        print("📚 Building knowledge base for first time...")
        build_vectorstore()
    else:
        print("⚠️ No books folder found — skipping knowledge base build")
else:
    print("✅ Knowledge base already exists!")