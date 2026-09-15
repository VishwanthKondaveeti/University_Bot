"""Pre-build the vector index at image-build time.

Render's free runtime instance has only 512 MB, which is not enough to bulk-embed
~5,600 chunks. Build machines have more headroom, so we index once during
buildCommand and bake the ChromaDB files into the image. At runtime the service
opens the existing collection and skips re-indexing.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from document_loader import DocumentLoader
from text_chunker import TextChunker
from embeddings_db import EmbeddingsDatabase

DOCS_DIR = os.getenv("DOCS_DIR", "../university_docs")
CHROMA_DIR = os.getenv("CHROMA_DIR", "../chroma_db")


def main():
    if not os.path.exists(DOCS_DIR):
        print(f"[build_index] {DOCS_DIR} not found - skipping index build")
        return

    db = EmbeddingsDatabase(persist_directory=CHROMA_DIR, insert_batch_size=100)
    if db.get_collection_count() > 0:
        print("[build_index] collection already populated - skipping")
        return

    documents = DocumentLoader().load_from_directory(DOCS_DIR, recursive=True)
    if not documents:
        print("[build_index] no documents loaded - skipping")
        return

    chunks = TextChunker(chunk_size=300, chunk_overlap=50).chunk_documents(documents)
    db.clear_collection()
    db.add_documents(chunks)
    print(f"[build_index] indexed {len(chunks)} chunks from {len(documents)} pages")


if __name__ == "__main__":
    main()
