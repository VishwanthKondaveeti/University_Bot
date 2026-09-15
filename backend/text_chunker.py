from typing import List
import re

class TextChunker:
    """Optimized text chunker for embedding and retrieval."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize the text chunker with optimized settings.
        
        Args:
            chunk_size: Maximum size of each chunk in characters (optimized for speed)
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: dict) -> List[dict]:
        """
        Split text into chunks with overlap using character-based splitting (faster).
        
        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunked documents with metadata
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundaries
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                sentence_end = text.rfind('.', start, end + 50)
                if sentence_end > start + 100:  # Ensure we don't make chunks too small
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunks.append({
                    'text': chunk_text,
                    'metadata': metadata.copy()
                })
            
            # Reached the end of the text — stop cleanly.
            if end >= text_length:
                break
            
            # Move start position with overlap, but guarantee forward progress
            # so we can never loop forever on short or pathological inputs.
            next_start = end - self.chunk_overlap
            if next_start <= start:
                next_start = start + 1
            start = next_start
        
        return chunks
    
    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk multiple documents efficiently.
        
        Args:
            documents: List of documents with text and metadata
            
        Returns:
            List of all chunked documents
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_text(doc['text'], doc['metadata'])
            all_chunks.extend(chunks)
        
        return all_chunks
