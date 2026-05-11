# startup.py
import os

DB_FOLDER = "./trading_db"

if os.path.exists(f"{DB_FOLDER}/chunks.pkl"):
    print("✅ Knowledge base already exists!")
else:
    print("❌ Knowledge base not found! Please run ingest.py locally and commit trading_db folder.")