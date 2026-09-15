from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
import os
import threading
import time
from dotenv import load_dotenv

# Import our modules
from document_loader import DocumentLoader
from text_chunker import TextChunker
from embeddings_db import EmbeddingsDatabase
from rag_system import RAGSystem

# Load environment variables
load_dotenv()

# Global instances
loader = DocumentLoader()
chunker = TextChunker(chunk_size=300, chunk_overlap=50)  # Highly optimized for speed
db = None
rag_system = None

# Deployment-configurable settings
DOCS_DIR = os.getenv("DOCS_DIR", "../university_docs")
AUTO_LOAD = os.getenv("AUTO_LOAD", "false").lower() in ("1", "true", "yes")

# Load-progress tracking (shared between background task and API)
load_state_lock = threading.Lock()
load_state = {
    "status": "idle",        # idle | loading | done | error
    "stage": "",             # human-readable current stage
    "documents": 0,          # number of PDF pages discovered
    "chunks": 0,             # number of chunks indexed
    "message": "",
    "error": "",
    "started_at": None,
    "finished_at": None,
}


def _set_load_state(**updates):
    with load_state_lock:
        load_state.update(updates)


def _snapshot_load_state():
    with load_state_lock:
        return dict(load_state)


def _run_document_load():
    """Read, chunk, embed, and index all PDFs in DOCS_DIR. Updates load_state."""
    global db, rag_system
    _set_load_state(
        status="loading",
        stage="Scanning documents",
        documents=0,
        chunks=0,
        message="",
        error="",
        started_at=time.time(),
        finished_at=None,
    )
    try:
        if not os.path.exists(DOCS_DIR):
            raise FileNotFoundError(f"Folder {DOCS_DIR} not found")

        _set_load_state(stage="Reading PDFs")
        documents = loader.load_from_directory(DOCS_DIR, recursive=True)
        if not documents:
            raise ValueError("No documents could be loaded")
        _set_load_state(documents=len(documents), stage="Chunking text")

        chunks = chunker.chunk_documents(documents)
        _set_load_state(chunks=len(chunks), stage="Embedding and indexing")

        if db is None:
            db = EmbeddingsDatabase()

        db.clear_collection()
        db.add_documents(chunks)

        api_key = os.getenv("GROQ_API_KEY", "")
        rag_system = RAGSystem(db, api_key=api_key if api_key else None)

        _set_load_state(
            status="done",
            stage="Ready",
            message=f"Loaded {len(documents)} pages into {len(chunks)} chunks",
            finished_at=time.time(),
        )
    except Exception as e:
        _set_load_state(
            status="error",
            stage="Failed",
            error=str(e),
            message=f"Error loading documents: {e}",
            finished_at=time.time(),
        )


def _init_backend():
    """Heavy startup work, run off the port-bind path so health checks pass fast."""
    global db, rag_system
    try:
        db = EmbeddingsDatabase()
        api_key = os.getenv("GROQ_API_KEY", "")
        rag_system = RAGSystem(db, api_key=api_key if api_key else None)
        print("Backend initialized successfully")

        # On deployed hosts the disk is often ephemeral, so optionally rebuild
        # the index automatically when the collection is empty.
        if AUTO_LOAD and db.get_collection_count() == 0:
            print("AUTO_LOAD enabled and index empty - loading documents in background")
            _run_document_load()
    except Exception as e:
        print(f"Backend initialization failed: {e}")
        _set_load_state(
            status="error",
            stage="Init failed",
            error=str(e),
            message=f"Backend initialization failed: {e}",
            finished_at=time.time(),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize on a background thread: opening Chroma and downloading the
    # embedding model can take minutes, and blocking here would prevent uvicorn
    # from binding its port before the host's health/port scan gives up.
    threading.Thread(target=_init_backend, daemon=True).start()
    yield
    # Shutdown
    print("Backend shutting down")

app = FastAPI(title="University RAG Backend", lifespan=lifespan)

# CORS middleware - restrict via ALLOWED_ORIGINS (comma-separated) in production.
_allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 8

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    found: bool

class DocumentStatus(BaseModel):
    documents_loaded: bool
    document_count: int
    chunk_count: int
    categories: dict
    load_status: str
    load_stage: str

class LoadProgress(BaseModel):
    status: str
    stage: str
    documents: int
    chunks: int
    message: str
    error: str
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


def _scan_categories(docs_folder: str) -> dict:
    categories = {}
    if os.path.exists(docs_folder):
        for root, _dirs, files in os.walk(docs_folder):
            for file in files:
                if file.lower().endswith('.pdf'):
                    rel_path = os.path.relpath(root, docs_folder)
                    category = rel_path if rel_path != '.' else 'General'
                    categories[category] = categories.get(category, 0) + 1
    return categories


@app.get("/")
async def root():
    return {"message": "University RAG Backend API", "status": "running"}

@app.get("/status", response_model=DocumentStatus)
async def get_status():
    """Get current document loading status."""
    chunk_count = db.get_collection_count() if db else 0
    categories = _scan_categories(DOCS_DIR)
    state = _snapshot_load_state()

    return DocumentStatus(
        documents_loaded=chunk_count > 0,
        document_count=state["documents"] or chunk_count,
        chunk_count=chunk_count,
        categories=categories,
        load_status=state["status"],
        load_stage=state["stage"],
    )


@app.get("/load-progress", response_model=LoadProgress)
async def get_load_progress():
    """Return the live state of the background document-loading job."""
    return LoadProgress(**_snapshot_load_state())


@app.post("/load-documents")
async def load_documents(background_tasks: BackgroundTasks):
    """Load documents from the configured docs folder (runs in background)."""
    state = _snapshot_load_state()
    if state["status"] == "loading":
        return {"message": "Document loading already in progress", "status": state["status"]}

    background_tasks.add_task(_run_document_load)
    return {"message": "Document loading started in background", "status": "loading"}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the loaded documents."""
    if rag_system is None:
        raise HTTPException(status_code=400, detail="Documents not loaded. Please load documents first.")

    if db is None or db.get_collection_count() == 0:
        raise HTTPException(status_code=400, detail="No documents in database. Please load documents first.")

    try:
        result = rag_system.answer_question(request.question, top_k=request.top_k)
        return QueryResponse(
            answer=result['answer'],
            sources=result['sources'],
            found=result['found']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/clear-documents")
async def clear_documents():
    """Clear all loaded documents."""
    global db, rag_system
    if db:
        db.clear_collection()
    _set_load_state(
        status="idle",
        stage="",
        documents=0,
        chunks=0,
        message="Cleared",
        error="",
        started_at=None,
        finished_at=time.time(),
    )
    return {"message": "Documents cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
