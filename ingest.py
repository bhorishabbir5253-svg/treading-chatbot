# ingest.py
import os
import shutil
import pickle
import pdfplumber
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

BOOKS_FOLDER = "./Books"
DB_FOLDER = "./trading_db"

def load_pdfs(folder):
    all_text = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder, filename)
            print(f"📖 Reading: {filename}")
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append({
                            "text": text,
                            "source": filename
                        })
    return all_text

def build_vectorstore():
    if os.path.exists(DB_FOLDER):
        print("🗑️ Deleting old knowledge base...")
        shutil.rmtree(DB_FOLDER)

    os.makedirs(DB_FOLDER)

    print("📚 Loading your trading books...")
    pages = load_pdfs(BOOKS_FOLDER)

    if not pages:
        print("❌ No PDF books found!")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    docs = []
    metadatas = []
    for page in pages:
        chunks = splitter.split_text(page["text"])
        for chunk in chunks:
            docs.append(chunk)
            metadatas.append({"source": page["source"]})

    print(f"✅ Total chunks: {len(docs)}")

    # Save chunks and metadata as pickle files
    with open(f"{DB_FOLDER}/chunks.pkl", "wb") as f:
        pickle.dump(docs, f)

    with open(f"{DB_FOLDER}/metadatas.pkl", "wb") as f:
        pickle.dump(metadatas, f)

    # Build TF-IDF index
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np

    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(docs)

    with open(f"{DB_FOLDER}/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    import scipy.sparse as sp
    sp.save_npz(f"{DB_FOLDER}/tfidf_matrix.npz", tfidf_matrix)

    print("🎉 Knowledge base saved successfully!")
    print(f"📚 Total books indexed: {len(set(m['source'] for m in metadatas))}")

if __name__ == "__main__":
    build_vectorstore()