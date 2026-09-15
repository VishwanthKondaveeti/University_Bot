import streamlit as st
import requests
import os
import time

# API Configuration
# Priority: BACKEND_URL env var > Streamlit secret > local default.
def _resolve_api_base_url() -> str:
    url = os.environ.get("BACKEND_URL")
    if not url:
        try:
            url = st.secrets.get("BACKEND_URL")
        except Exception:
            url = None
    return (url or "http://localhost:8000").rstrip("/")

API_BASE_URL = _resolve_api_base_url()

# Page configuration
st.set_page_config(
    page_title="Vignan University Knowledge Assistant",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
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
        margin-top: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .answer-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-top: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    .welcome-box h2 { color: white; margin-top: 0; }
    .history-q {
        font-weight: 600;
        color: #1e3a8a;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ----- Session state -----
defaults = {
    "api_connected": False,
    "documents_loaded": False,
    "history": [],          # list of dicts: {question, answer, sources, found}
    "top_k": 8,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ----- API helpers -----
def check_api_connection():
    try:
        r = requests.get(f"{API_BASE_URL}/", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def get_status():
    try:
        r = requests.get(f"{API_BASE_URL}/status", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def get_load_progress():
    try:
        r = requests.get(f"{API_BASE_URL}/load-progress", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def load_documents():
    try:
        r = requests.post(f"{API_BASE_URL}/load-documents", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def clear_documents():
    try:
        r = requests.post(f"{API_BASE_URL}/clear-documents", timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def query_documents(question: str, top_k: int = 5):
    try:
        r = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()
        return {"error": r.text}
    except Exception as e:
        return {"error": str(e)}


def wait_for_load(timeout_seconds: int = 300, poll_every: float = 1.5):
    """Poll /load-progress until the background job finishes (or times out)."""
    started = time.time()
    progress_bar = st.progress(0.0, text="Starting…")
    status_text = st.empty()
    while time.time() - started < timeout_seconds:
        prog = get_load_progress()
        if not prog:
            status_text.warning("Lost contact with backend while loading.")
            time.sleep(poll_every)
            continue
        status = prog.get("status")
        stage = prog.get("stage") or ""
        docs = prog.get("documents") or 0
        chunks = prog.get("chunks") or 0
        msg = prog.get("message") or prog.get("error") or ""

        # Rough progress estimate from pipeline stages.
        stage_weight = {
            "Scanning university_docs": 0.05,
            "Reading PDFs": 0.25,
            "Chunking text": 0.45,
            "Embedding and indexing": 0.75,
            "Ready": 1.0,
            "Failed": 1.0,
        }.get(stage, 0.1)
        progress_bar.progress(min(stage_weight, 1.0), text=f"{stage} — {docs} pages, {chunks} chunks")
        status_text.info(msg or f"{stage}…")

        if status == "done":
            progress_bar.progress(1.0, text="Done")
            status_text.success(msg or "Documents loaded.")
            return True
        if status == "error":
            progress_bar.empty()
            status_text.error(msg or "Document loading failed.")
            return False
        time.sleep(poll_every)
    status_text.error("Timed out waiting for documents to load.")
    return False


# ----- Header -----
st.markdown('<div class="main-header">🎓 Vignan University Knowledge Assistant</div>', unsafe_allow_html=True)

st.session_state.api_connected = check_api_connection()
if not st.session_state.api_connected:
    st.error("❌ Backend API not connected. Please start the backend server first.")
    st.info("Run: `start_backend.bat`  (or `cd backend && python main.py`)")
    st.stop()

st.markdown("""
<div class="welcome-box">
    <h2>Welcome to Your University Knowledge Base</h2>
    <p>Get instant answers to questions about regulations, policies, academic rules, and guidelines.</p>
</div>
""", unsafe_allow_html=True)

# ----- Sidebar -----
with st.sidebar:
    st.header("📚 Knowledge Base")
    status = get_status()

    if status:
        st.session_state.documents_loaded = status["documents_loaded"]

        st.subheader("📁 Document Categories")
        if status["categories"]:
            for category, count in sorted(status["categories"].items()):
                with st.expander(f"📂 {category} ({count} files)"):
                    st.text(f"Contains {count} PDF files")
            st.markdown(f"**Total Categories:** {len(status['categories'])}")
        else:
            st.warning("No document categories found")

        st.markdown("---")
        st.subheader("📊 Database Status")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""<div class="stat-card">
                    <h3 style="margin:0;color:#1e3a8a;">{status['chunk_count']}</h3>
                    <p style="margin:0;color:#6b7280;">Chunks</p>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            badge = "✅" if status["documents_loaded"] else "❌"
            st.markdown(
                f"""<div class="stat-card">
                    <h3 style="margin:0;color:#1e3a8a;">{badge}</h3>
                    <p style="margin:0;color:#6b7280;">Loaded</p>
                </div>""",
                unsafe_allow_html=True,
            )

        st.caption(f"Load status: **{status.get('load_status','idle')}** {status.get('load_stage','')}")

        st.markdown("---")
        st.subheader("🔄 Document Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load All", type="primary", use_container_width=True):
                if load_documents():
                    wait_for_load()
                    st.rerun()
                else:
                    st.error("❌ Failed to start document loading")
        with col2:
            if st.button("Clear", use_container_width=True):
                if clear_documents():
                    st.session_state.history = []
                    st.success("✅ Documents cleared!")
                    st.rerun()
                else:
                    st.error("❌ Failed to clear documents")

        st.markdown("---")
        st.subheader("💬 Chat")
        if st.button("Clear chat history", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.warning("Could not fetch status from backend")

# ----- Main Q&A -----
st.markdown('<div class="sub-header">❓ Ask Your Question</div>', unsafe_allow_html=True)

if not st.session_state.documents_loaded:
    st.info("👈 Please load documents from the sidebar to start asking questions.")
else:
    question = st.text_area(
        "Type your question about university regulations, policies, or academic guidelines:",
        placeholder="e.g., What is the minimum attendance requirement for B.Tech students?",
        height=120,
        key="question_input",
    )

    with st.expander("⚙️ Advanced Options"):
        st.session_state.top_k = st.slider(
            "Number of sources to use", min_value=1, max_value=10, value=st.session_state.top_k
        )

    ask_button = st.button("🔍 Get Answer", type="primary", use_container_width=True)

    if ask_button and question.strip():
        with st.spinner("🤔 Processing your question…"):
            result = query_documents(question.strip(), top_k=st.session_state.top_k)

        if result and "error" not in result:
            st.session_state.history.append({
                "question": question.strip(),
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "found": result.get("found", False),
            })
            st.rerun()
        elif result and "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.error("❌ Error processing your question. Please try again.")

    # ----- History -----
    if st.session_state.history:
        st.markdown('<div class="sub-header">🗂 Conversation</div>', unsafe_allow_html=True)
        # Show newest first.
        for turn in reversed(st.session_state.history):
            st.markdown(f'<div class="history-q">Q: {turn["question"]}</div>', unsafe_allow_html=True)
            if turn["found"]:
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(turn["answer"])
                st.markdown('</div>', unsafe_allow_html=True)
                if turn["sources"]:
                    with st.expander(f"📖 Sources ({len(turn['sources'])})"):
                        for src in turn["sources"]:
                            category = src.get("category", "General")
                            st.markdown(
                                f"""<div class="source-box">
                                    <span class="category-badge">{category}</span>
                                    <strong>📄 {src.get('source','Unknown')}</strong>
                                    &nbsp;·&nbsp; <strong>📖 Page {src.get('page','?')}</strong>
                                </div>""",
                                unsafe_allow_html=True,
                            )
            else:
                st.markdown('<div class="not-found">', unsafe_allow_html=True)
                st.markdown("### ⚠️ Information Not Found")
                st.write(turn["answer"])
                st.markdown('</div>', unsafe_allow_html=True)

# ----- Footer -----
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#6b7280;font-size:0.9rem;'>
    <p>Built with RAG — ChromaDB · Sentence Transformers · Groq Llama3</p>
</div>
""", unsafe_allow_html=True)
