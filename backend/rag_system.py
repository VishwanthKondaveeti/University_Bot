from typing import List, Dict, Optional
import os
from embeddings_db import EmbeddingsDatabase
from groq import Groq

class RAGSystem:
    """RAG system for answering questions from university regulations."""
    
    def __init__(self, db: EmbeddingsDatabase, api_key: str = None):
        """
        Initialize the RAG system.
        
        Args:
            db: EmbeddingsDatabase instance
            api_key: Groq API key for LLM access
        """
        self.db = db
        self.api_key = api_key
        self.client = None
        # Model is configurable so the app survives Groq model deprecations.
        self.model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: User query
            top_k: Number of top results to retrieve
            
        Returns:
            List of relevant document chunks
        """
        results = self.db.query(query, n_results=top_k)
        return results
    
    def generate_answer(self, query: str, context: List[Dict]) -> Dict:
        """
        Generate an answer based on retrieved context.
        
        Args:
            query: User query
            context: Retrieved document chunks
            
        Returns:
            Dictionary containing answer and source information
        """
        if not context:
            return {
                'answer': "I cannot find relevant information in the uploaded documents to answer your question.",
                'sources': [],
                'found': False
            }
        
        # Check if the context is relevant enough
        relevance_threshold = 0.8  # Distance threshold (lower is more similar)
        relevant_docs = [doc for doc in context if doc['distance'] < relevance_threshold]
        
        if not relevant_docs:
            return {
                'answer': "I cannot find sufficiently relevant information in the uploaded documents to answer your question.",
                'sources': [],
                'found': False
            }
        
        # Collect sources from relevant documents
        sources = []
        for doc in relevant_docs[:5]:  # Use top 5 most relevant for sources
            source_info = {
                'source': doc['metadata'].get('source', 'Unknown'),
                'page': doc['metadata'].get('page'),
                'file_path': doc['metadata'].get('file_path'),
                'category': doc['metadata'].get('category', 'General'),
            }
            if source_info not in sources:
                sources.append(source_info)
        
        # Use LLM if available, otherwise use simple method
        if self.client:
            return self._generate_llm_answer(query, relevant_docs, sources)
        else:
            return self._generate_simple_answer(relevant_docs, sources)
    
    def _generate_llm_answer(self, query: str, relevant_docs: List[Dict], sources: List[Dict]) -> Dict:
        """
        Generate answer using LLM.
        
        Args:
            query: User query
            relevant_docs: Relevant document chunks
            sources: Source information
            
        Returns:
            Dictionary with LLM-generated answer and sources
        """
        # Prepare context for LLM with better formatting
        context_text = "\n\n".join([
            f"--- Document: {doc['metadata'].get('source', 'Unknown')} | Page: {doc['metadata']['page']} | Category: {doc['metadata'].get('category', 'General')} ---\n{doc['text']}"
            for doc in relevant_docs
        ])
        
        # Create enhanced prompt for LLM
        prompt = f"""You are an expert university knowledge assistant specializing in academic regulations, policies, and guidelines. Your role is to provide accurate, helpful answers based on the provided document context.

CONTEXT INFORMATION:
{context_text}

USER QUESTION: {query}

ANSWER GUIDELINES:
1. Answer ONLY using information from the provided context
2. If the context doesn't contain sufficient information, clearly state this
3. Structure your answer with clear headings and bullet points when appropriate
4. Include specific details like percentages, requirements, procedures, etc.
5. Cite the specific document and page number for each piece of information
6. Be concise but comprehensive - focus on the most relevant information
7. If information is conflicting or unclear in the context, mention this
8. For policy questions, include the exact requirements or rules mentioned
9. For procedural questions, include step-by-step instructions if available
10. Maintain a professional, helpful tone

FORMAT YOUR ANSWER AS:
- Start with a direct answer summary
- Follow with detailed explanation
- Include specific requirements or rules as bullet points
- End with source citations

Answer:"""

        try:
            # Call Groq API with optimized parameters for speed
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert university knowledge assistant specializing in academic regulations, policies, examination guidelines, and student handbook information. Provide accurate, well-structured answers based on the provided context."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower for more focused answers
                max_tokens=1024,  # Optimized for speed
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'sources': sources,
                'found': True
            }
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Fall back to simple answer generation
            return self._generate_simple_answer(relevant_docs, sources)
    
    def _generate_simple_answer(self, relevant_docs: List[Dict], sources: List[Dict]) -> Dict:
        """
        Generate answer using simple context concatenation (fallback method).
        
        Args:
            relevant_docs: Relevant document chunks
            sources: Source information
            
        Returns:
            Dictionary with simple answer and sources
        """
        # Construct answer from most relevant chunks
        answer_parts = []
        
        for doc in relevant_docs[:3]:  # Use top 3 most relevant
            answer_parts.append(doc['text'])
        
        answer = "Based on the uploaded documents, here is the relevant information:\n\n"
        answer += "\n\n".join(answer_parts)
        
        return {
            'answer': answer,
            'sources': sources,
            'found': True
        }
    
    def answer_question(self, query: str, top_k: int = 5) -> Dict:
        """
        Complete pipeline to answer a question.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and source information
        """
        # Retrieve relevant context
        context = self.retrieve_relevant_context(query, top_k)
        
        # Generate answer
        result = self.generate_answer(query, context)
        
        return result
