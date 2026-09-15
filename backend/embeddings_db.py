import chromadb
from typing import List, Dict
import os
import uuid

class EmbeddingsDatabase:
    """Embeddings storage and retrieval using ChromaDB's built-in ONNX embedder.

    Chroma's default embedding function (ONNX all-MiniLM-L6-v2) produces the same
    embeddings as the sentence-transformers model but without PyTorch, keeping the
    memory footprint small enough for 512 MB hosts (e.g. Render free tier).
    """

    def __init__(self, collection_name: str = "university_regulations", persist_directory: str = None, insert_batch_size: int = 100):
        """
        Initialize the embeddings database.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database. Defaults to the
                CHROMA_DIR env var, or "../chroma_db" when unset (local dev).
            insert_batch_size: Max items per ChromaDB add() call (Chroma caps around 5461)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or os.getenv("CHROMA_DIR", "../chroma_db")
        self.insert_batch_size = insert_batch_size

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)

        # Get or create collection; embeddings are produced by Chroma's default
        # ONNX embedding function on add()/query(), so no torch model is loaded here.
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, chunks: List[dict]) -> None:
        """
        Add document chunks to the database in safe batches.

        ChromaDB rejects a single add() call above ~5461 items, so we slice the
        input into insert_batch_size windows. Chroma embeds each window internally.

        Args:
            chunks: List of chunked documents with text and metadata
        """
        if not chunks:
            print("No chunks to add to database")
            return

        total = len(chunks)
        batch_size = max(1, self.insert_batch_size)
        added = 0

        for start in range(0, total, batch_size):
            window = chunks[start:start + batch_size]
            texts = [c['text'] for c in window]
            metadatas = [c['metadata'] for c in window]
            ids = [str(uuid.uuid4()) for _ in window]

            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            added += len(window)
            print(f"Indexed {added}/{total} chunks")

        print(f"Added {total} chunks to database")

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the database for relevant documents.

        Args:
            query_text: The query text
            n_results: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return formatted_results

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print("Collection cleared")

    def get_collection_count(self) -> int:
        """Return the number of documents in the collection."""
        return self.collection.count()
