import os
from typing import List
from pypdf import PdfReader

class DocumentLoader:
    """Load and preprocess PDF documents for the RAG system."""
    
    def __init__(self):
        self.documents = []
    
    def load_pdf(self, file_path: str, base_dir: str = None) -> List[dict]:
        """
        Load a single PDF file and extract text with metadata.
        
        Args:
            file_path: Path to the PDF file
            base_dir: Root directory used to compute the relative category. When
                None, falls back to the file's own directory name.
            
        Returns:
            List of dictionaries containing text and metadata
        """
        try:
            reader = PdfReader(file_path)
            documents = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    if base_dir:
                        rel_path = os.path.relpath(file_path, base_dir)
                    else:
                        rel_path = os.path.basename(file_path)
                    rel_dir = os.path.dirname(rel_path)
                    
                    documents.append({
                        'text': text,
                        'metadata': {
                            'source': os.path.basename(file_path),
                            'page': page_num + 1,
                            'file_path': file_path,
                            'category': rel_dir if rel_dir else 'General'
                        }
                    })
            
            return documents
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            return []
    
    def load_multiple_pdfs(self, file_paths: List[str]) -> List[dict]:
        """
        Load multiple PDF files.
        
        Args:
            file_paths: List of paths to PDF files
            
        Returns:
            List of all documents from all PDFs
        """
        all_documents = []
        
        for file_path in file_paths:
            documents = self.load_pdf(file_path)
            all_documents.extend(documents)
        
        self.documents = all_documents
        return all_documents
    
    def load_from_directory(self, directory: str, recursive: bool = True) -> List[dict]:
        """
        Load all PDF files from a directory (optionally recursive).
        
        Args:
            directory: Path to the directory
            recursive: Whether to search subdirectories
            
        Returns:
            List of all documents from all PDFs in the directory
        """
        all_documents = []
        pdf_files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
        else:
            # Only load from the specified directory
            for file in os.listdir(directory):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(directory, file))
        
        # Load all PDF files
        for file_path in pdf_files:
            documents = self.load_pdf(file_path, base_dir=directory)
            all_documents.extend(documents)
        
        self.documents = all_documents
        return all_documents
    
    def get_document_count(self) -> int:
        """Return the total number of loaded documents."""
        return len(self.documents)
