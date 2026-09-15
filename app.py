import streamlit as st
import os
from collections import defaultdict
from dotenv import load_dotenv
from document_loader import DocumentLoader
from text_chunker import TextChunker
from embeddings_db import EmbeddingsDatabase
from rag_system import RAGSystem

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="University Regulation RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .source-box {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border-left: 4px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .source-box:hover {
        background-color: #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .answer-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-top: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .answer-box h3 {
        color: white;
        margin-top: 0;
    }
    .not-found {
        background-color: #fef2f2;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border: 1px solid #fecaca;
        border-left: 4px solid #ef4444;
    }
    .stat-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #dbeafe;
        color: #1e40af;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0.75rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .welcome-box h2 {
        color: white;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'document_count' not in st.session_state:
    st.session_state.document_count = 0
if 'chunk_count' not in st.session_state:
    st.session_state.chunk_count = 0

# Main header
st.markdown('<div class="main-header">🎓 Vignan University Knowledge Assistant</div>', unsafe_allow_html=True)

# Welcome box
st.markdown("""
<div class="welcome-box">
    <h2>Welcome to Your University Knowledge Base</h2>
    <p>Get instant answers to questions about regulations, policies, academic rules, and guidelines.</p>
    <p><strong>Documents covered:</strong> Academic Regulations, Policies, Exam Guidelines, Attendance Rules, and more</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for document management
with st.sidebar:
    st.header("� Knowledge Base")
    
    # Check for university_docs folder
    docs_folder = "university_docs"
    
    # Document categories
    st.subheader("📁 Document Categories")
    
    categories = {}
    total_files = 0
    
    if os.path.exists(docs_folder):
        # Walk through directory to get categories
        for root, dirs, files in os.walk(docs_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    total_files += 1
                    rel_path = os.path.relpath(root, docs_folder)
                    category = rel_path if rel_path != '.' else 'General'
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(file)
        
        # Display categories
        for category, files in sorted(categories.items()):
            with st.expander(f"📂 {category} ({len(files)} files)"):
                for file in sorted(files):
                    st.text(f"📄 {file}")
        
        st.markdown(f"**Total PDF Files:** {total_files}")
        
        # Load documents button
        st.markdown("---")
        st.subheader("🔄 Document Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load All", type="primary", use_container_width=True, key="load_all_button"):
                try:
                    with st.spinner("📄 Loading documents from university_docs..."):
                        loader = DocumentLoader()
                        documents = loader.load_from_directory(docs_folder, recursive=True)
                        
                        if not documents:
                            st.error("❌ No text could be extracted from the PDF files.")
                        else:
                            st.info(f"📊 Loaded {len(documents)} pages from {total_files} files")
                    
                    with st.spinner("✂️ Creating text chunks..."):
                        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
                        chunks = chunker.chunk_documents(documents)
                        st.info(f"📦 Created {len(chunks)} chunks")
                    
                    with st.spinner("🧠 Generating embeddings and building database..."):
                        db = EmbeddingsDatabase()
                        db.clear_collection()
                        db.add_documents(chunks)
                        st.info("💾 Database updated")
                    
                    api_key = os.getenv("GROQ_API_KEY", "")
                    
                    st.session_state.documents_loaded = True
                    st.session_state.document_count = len(documents)
                    st.session_state.chunk_count = len(chunks)
                    st.session_state.db = db
                    st.session_state.api_key = api_key
                    st.session_state.rag_system = RAGSystem(db, api_key=api_key if api_key else None)
                    
                    st.success(f"✅ Successfully loaded {len(documents)} pages from {total_files} files!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error loading documents: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
        
        with col2:
            if st.button("Clear", use_container_width=True):
                if 'db' in st.session_state:
                    st.session_state.db.clear_collection()
                st.session_state.documents_loaded = False
                st.session_state.document_count = 0
                st.session_state.chunk_count = 0
                st.rerun()
        
        # Additional file upload
        st.markdown("---")
        st.subheader("➕ Add More Documents")
        
        uploaded_files = st.file_uploader(
            "Upload additional PDFs",
            type=['pdf'],
            accept_multiple_files=True,
            help="Add more documents to the knowledge base"
        )
        
        if uploaded_files:
            if st.button("Process Uploads", use_container_width=True):
                with st.spinner("Processing uploaded documents..."):
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                    
                    loader = DocumentLoader()
                    new_documents = loader.load_multiple_pdfs(file_paths)
                    
                    if new_documents:
                        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
                        new_chunks = chunker.chunk_documents(new_documents)
                        
                        if 'db' in st.session_state:
                            st.session_state.db.add_documents(new_chunks)
                        else:
                            db = EmbeddingsDatabase()
                            db.add_documents(new_chunks)
                            st.session_state.db = db
                        
                        st.session_state.document_count += len(new_documents)
                        st.session_state.chunk_count += len(new_chunks)
                        
                        st.success(f"✅ Added {len(new_documents)} pages from {len(uploaded_files)} files!")
                        st.rerun()
                    else:
                        st.error("❌ No text could be extracted from the uploaded PDFs.")
    
    else:
        st.warning(f"📁 Folder '{docs_folder}' not found")
        st.info("Please create a 'university_docs' folder and add PDF files")
    
    # Display status
    if st.session_state.documents_loaded:
        st.markdown("---")
        st.subheader("📊 Knowledge Base Status")
        
        # Statistics cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color:#1e3a8a;">{st.session_state.document_count}</h3>
                <p style="margin:0; color:#6b7280;">Pages Loaded</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <h3 style="margin:0; color:#1e3a8a;">{st.session_state.chunk_count}</h3>
                <p style="margin:0; color:#6b7280;">Chunks Indexed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show LLM status
        if st.session_state.api_key:
            st.success("🤖 AI-Powered Answers Enabled")
        else:
            st.info("📝 Basic Mode (No AI)")
        
        if st.button("🔄 Reload Knowledge Base", use_container_width=True):
            if os.path.exists(docs_folder):
                with st.spinner("Reloading documents..."):
                    loader = DocumentLoader()
                    documents = loader.load_from_directory(docs_folder, recursive=True)
                    
                    if documents:
                        chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
                        chunks = chunker.chunk_documents(documents)
                        
                        db = EmbeddingsDatabase()
                        db.clear_collection()
                        db.add_documents(chunks)
                        
                        api_key = os.getenv("GROQ_API_KEY", "")
                        
                        st.session_state.documents_loaded = True
                        st.session_state.document_count = len(documents)
                        st.session_state.chunk_count = len(chunks)
                        st.session_state.db = db
                        st.session_state.api_key = api_key
                        st.session_state.rag_system = RAGSystem(db, api_key=api_key if api_key else None)
                        
                        st.success(f"✅ Reloaded {len(documents)} pages!")
                        st.rerun()
            else:
                st.error(f"Folder '{docs_folder}' not found")

# Main Q&A interface
st.markdown('<div class="sub-header">❓ Ask Your Question</div>', unsafe_allow_html=True)

# Check if documents are loaded
if not st.session_state.documents_loaded:
    st.info("👈 Please load documents from the sidebar to start asking questions.")
else:
    # Question input with better styling
    question = st.text_area(
        "Type your question about university regulations, policies, or academic guidelines:",
        placeholder="e.g., What is the minimum attendance requirement for B.Tech students? or What are the exam rules for MBA students?",
        height=120,
        key="question_input"
    )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider("Number of sources to use", min_value=1, max_value=10, value=5)
        with col2:
            use_ai = st.checkbox("Use AI-powered answers", value=True, help="Enable for more natural, comprehensive answers")
    
    # Ask button
    ask_button = st.button("🔍 Get Answer", type="primary", use_container_width=True, key="ask_button")
    
    if ask_button and question:
        with st.spinner("🤔 Analyzing your question and searching the knowledge base..."):
            # Get answer from RAG system
            result = st.session_state.rag_system.answer_question(question, top_k=top_k)
            
            # Display answer
            if result['found']:
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### 💡 Answer")
                st.markdown(result['answer'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Display sources with categories
                if result['sources']:
                    st.markdown('<div class="sub-header">📖 Sources & References</div>', unsafe_allow_html=True)
                    
                    # Group sources by category if available
                    sources_by_category = defaultdict(list)
                    for source in result['sources']:
                        category = source.get('category', 'General')
                        sources_by_category[category].append(source)
                    
                    for category, sources in sorted(sources_by_category.items()):
                        st.markdown(f"**{category}**")
                        for i, source in enumerate(sources, 1):
                            category_badge = f'<span class="category-badge">{source.get("category", "General")}</span>'
                            st.markdown(f"""
                            <div class="source-box">
                                {category_badge}
                                <strong>📄 {source['source']}</strong><br/>
                                <strong>📖 Page {source['page']}</strong>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="not-found">', unsafe_allow_html=True)
                st.markdown("### ⚠️ Information Not Found")
                st.write(result['answer'])
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Helpful suggestions
                st.markdown("### 💡 Suggestions")
                st.markdown("""
                - Try rephrasing your question with different keywords
                - Check if the topic is covered in the uploaded documents
                - Upload additional relevant documents to the knowledge base
                - Try asking a more specific question
                """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
    <p>Built with RAG (Retrieval-Augmented Generation) technology</p>
    <p>Uses ChromaDB for vector storage, Sentence Transformers for embeddings, and Groq for LLM-powered answers</p>
</div>
""", unsafe_allow_html=True)
