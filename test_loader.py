from document_loader import DocumentLoader
from text_chunker import TextChunker
from embeddings_db import EmbeddingsDatabase
import os

# Test the document loading
docs_folder = "university_docs"

if os.path.exists(docs_folder):
    print(f"Testing document loading from {docs_folder}...")
    
    loader = DocumentLoader()
    documents = loader.load_from_directory(docs_folder, recursive=True)
    
    print(f"Loaded {len(documents)} pages")
    
    if documents:
        print(f"Sample document metadata: {documents[0]['metadata']}")
        print(f"Sample text preview: {documents[0]['text'][:200]}...")
        
        # Test chunking
        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        # Test database
        db = EmbeddingsDatabase()
        db.clear_collection()
        db.add_documents(chunks)
        print(f"Database now has {db.get_collection_count()} documents")
        
        print("✅ All tests passed!")
    else:
        print("❌ No documents loaded")
else:
    print(f"❌ Folder {docs_folder} not found")
