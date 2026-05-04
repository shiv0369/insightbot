import os
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


# ============================================================
# CONFIGURATION
# ============================================================
PDF_FOLDER = "data/reports"
CHROMA_DB_PATH = "chroma_db"
COLLECTION_NAME = "business_reports"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, runs on CPU


# ============================================================
# STEP 1: Load the embedding model (only once)
# ============================================================
print("📦 Loading embedding model (first run downloads ~80MB)...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("   ✅ Embedding model ready.")


# ============================================================
# STEP 2: Read text from a PDF
# ============================================================
def read_pdf(filepath: str) -> str:
    """Extract all text from a single PDF."""
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# ============================================================
# STEP 3: Chunk the text into smaller pieces
# ============================================================
def chunk_text(text: str, source: str) -> list:
    """
    Split long text into chunks of ~500 characters with 50 char overlap.
    Overlap helps preserve context across chunk boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]  # try to split on natural boundaries
    )
    chunks = splitter.split_text(text)
    
    # Each chunk gets metadata so we know which file it came from
    return [
        {"text": chunk, "source": source, "chunk_id": f"{source}_{i}"}
        for i, chunk in enumerate(chunks)
    ]


# ============================================================
# STEP 4: Build the vector store from all PDFs
# ============================================================
def build_vector_store():
    """
    Reads all PDFs, chunks them, embeds them, stores in ChromaDB.
    Run this once whenever PDFs change.
    """
    print(f"\n🔨 Building vector store from {PDF_FOLDER}...")
    
    # Initialize ChromaDB client (data persists on disk)
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Delete existing collection if it exists (so we start fresh)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("   🗑️  Deleted old collection.")
    except Exception:
        pass
    
    # Create a new collection
    collection = client.create_collection(name=COLLECTION_NAME)
    
    # Read and chunk all PDFs
    all_chunks = []
    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))
    
    if not pdf_files:
        print(f"   ⚠️  No PDFs found in {PDF_FOLDER}!")
        return
    
    for pdf_path in pdf_files:
        print(f"   📄 Reading {pdf_path.name}...")
        text = read_pdf(str(pdf_path))
        chunks = chunk_text(text, source=pdf_path.name)
        all_chunks.extend(chunks)
        print(f"      → {len(chunks)} chunks")
    
    print(f"\n   📊 Total chunks: {len(all_chunks)}")
    print("   🧮 Generating embeddings...")
    
    # Embed all chunks at once (fast batch processing)
    texts = [c["text"] for c in all_chunks]
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    
    # Store in ChromaDB
    collection.add(
        ids=[c["chunk_id"] for c in all_chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{"source": c["source"]} for c in all_chunks]
    )
    
    print(f"\n   ✅ Stored {len(all_chunks)} chunks in ChromaDB.")
    return collection


# ============================================================
# STEP 5: Search for relevant chunks given a question
# ============================================================
def search_relevant_context(question: str, top_k: int = 3) -> list:
    """
    Given a question, find the top_k most relevant chunks from the PDFs.
    Returns a list of dicts with 'text' and 'source'.
    """
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Embed the question
    question_embedding = embedding_model.encode([question])[0].tolist()
    
    # Search for closest chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )
    
    # Format results
    relevant_chunks = []
    for i in range(len(results["documents"][0])):
        relevant_chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })
    
    return relevant_chunks


# ============================================================
# RUN: Build the vector store
# ============================================================
if __name__ == "__main__":
    
    # Build the vector store from PDFs
    build_vector_store()
    
    # Test: search for a sample question
    print("\n" + "="*65)
    print("🧪 TEST: Searching for relevant chunks")
    print("="*65)
    
    test_question = "Why did the East region sales drop?"
    print(f"\n❓ Question: {test_question}\n")
    
    chunks = search_relevant_context(test_question, top_k=3)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"📌 Match #{i} (from {chunk['source']}, distance={chunk['distance']:.3f}):")
        print(f"   {chunk['text'][:250]}...\n")