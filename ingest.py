# ingest.py
import os
import shutil
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

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
    # ✅ Delete old database first to avoid duplicates
    if os.path.exists(DB_FOLDER):
        print("🗑️  Deleting old knowledge base to avoid duplicates...")
        shutil.rmtree(DB_FOLDER)
        print("✅ Old data cleared!")

    print("📚 Loading your trading books...")
    pages = load_pdfs(BOOKS_FOLDER)

    if not pages:
        print("❌ No PDF books found in the /books folder!")
        print("   Please add your trading PDF books to the /books folder first.")
        return

    # Split into chunks
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

    print(f"✅ Total chunks created: {len(docs)}")

    print("🧠 Creating embeddings (this may take a few minutes)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=DB_FOLDER
    )
    vectorstore.persist()

    print(f"\n🎉 Done! Knowledge base saved with {len(docs)} chunks.")
    print(f"📚 Books indexed: {len(set(m['source'] for m in metadatas))}")
    for book in set(m['source'] for m in metadatas):
        print(f"   ✅ {book}")

if __name__ == "__main__":
    build_vectorstore()