# ingest.py
import os
import shutil
import pickle
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer

BOOKS_FOLDER = "./Books"
DB_FOLDER = "./trading_db"

def load_pdfs(folder):
    all_text = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            print(f"📖 Reading: {filename}")
            with pdfplumber.open(os.path.join(folder, filename)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        all_text.append({
                            "text": text.strip(),
                            "source": filename
                        })
    return all_text

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def build_vectorstore():
    if os.path.exists(DB_FOLDER):
        print("🗑️ Deleting old knowledge base...")
        shutil.rmtree(DB_FOLDER)
    os.makedirs(DB_FOLDER)

    print("📚 Loading your trading books...")
    pages = load_pdfs(BOOKS_FOLDER)

    if not pages:
        print("❌ No books found!")
        return

    docs = []
    metadatas = []
    for page in pages:
        for chunk in chunk_text(page["text"]):
            if len(chunk.strip()) > 30:
                docs.append(chunk.strip())
                metadatas.append(page["source"])

    print(f"✅ Total chunks: {len(docs)}")

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    vectorizer.fit(docs)

    with open(f"{DB_FOLDER}/chunks.pkl", "wb") as f:
        pickle.dump(docs, f)
    with open(f"{DB_FOLDER}/metadatas.pkl", "wb") as f:
        pickle.dump(metadatas, f)
    with open(f"{DB_FOLDER}/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    print("🎉 Knowledge base saved!")

if __name__ == "__main__":
    build_vectorstore()