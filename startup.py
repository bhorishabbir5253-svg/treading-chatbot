# startup.py
import os
from ingest import build_vectorstore

DB_FOLDER = "./trading_db"

# Build knowledge base on first startup if it doesn't exist
if not os.path.exists(DB_FOLDER):
    print("📚 Building knowledge base for first time...")
    build_vectorstore()
else:
    print("✅ Knowledge base already exists!")