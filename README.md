# Vignan University Knowledge Assistant

An AI-powered RAG (Retrieval-Augmented Generation) assistant with separated frontend/backend architecture for answering questions about university regulations, academic policies, examination guidelines, and student handbooks.

## 🏗️ Architecture Overview

This project uses a modern **frontend/backend separation**:

- **Backend**: FastAPI server for document processing, vector database, and LLM integration
- **Frontend**: Streamlit web interface for user interaction
- **Communication**: REST API between frontend and backend

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.env` file in the `backend/` directory:
```
GROQ_API_KEY=your_api_key_here
```

### 3. Start the Services

**Windows (using batch files):**
```bash
# Terminal 1: Start Backend
start_backend.bat

# Terminal 2: Start Frontend  
start_frontend.bat
```

**Manual:**
```bash
# Terminal 1: Start Backend
cd backend
python main.py

# Terminal 2: Start Frontend
cd frontend
streamlit run app.py
```

### 4. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Key Features

### 🚀 Performance Optimized
- **Fast Chunking**: Character-based chunking (300 chars, 50 overlap) for 3-5x speed improvement
- **Optimized LLM**: Llama3-8b for fast, intelligent responses
- **Batch Processing**: Efficient embeddings generation
- **Background Tasks**: Non-blocking document loading

### 🎨 Modern Frontend
- **Gradient UI Design**: Beautiful purple/blue gradient theme
- **Real-time Status**: Live updates from backend
- **Category Organization**: Visual document categorization
- **Responsive Layout**: Works on all screen sizes

### 🔧 Robust Backend
- **REST API**: Clean endpoints for all operations
- **Error Handling**: Comprehensive error management
- **Background Processing**: Document loading doesn't block API
- **Vector Database**: ChromaDB with optimized operations

## 📁 Project Structure

```
Uni_Bot/
├── backend/                    # FastAPI Backend
│   ├── main.py                # API endpoints
│   ├── document_loader.py     # PDF processing
│   ├── text_chunker.py        # Optimized chunking
│   ├── embeddings_db.py       # Vector database
│   ├── rag_system.py          # RAG + LLM
│   ├── requirements.txt       # Backend deps
│   └── .env                   # API keys
├── frontend/                   # Streamlit Frontend
│   ├── app.py                 # Web UI
│   └── requirements.txt       # Frontend deps
├── university_docs/            # Document storage
│   ├── policies/
│   ├── regulations/
│   └── *.pdf
├── chroma_db/                 # Vector storage
├── start_backend.bat          # Backend startup script
├── start_frontend.bat         # Frontend startup script
└── README_ARCHITECTURE.md      # Detailed architecture docs
```

## 📡 API Endpoints

### `GET /` 
Health check endpoint

### `GET /status`
Get current system status (documents loaded, categories, etc.)

### `POST /load-documents`
Load and process documents from university_docs folder (runs in background)

### `GET /load-progress`
Live status of the background loading job (`status`, `stage`, `documents`, `chunks`, `error`). The frontend polls this to show a real progress bar.

### `POST /query`
Query the knowledge base
```json
{
  "question": "What is the attendance requirement?",
  "top_k": 5
}
```

### `POST /clear-documents`
Clear all documents from the database

## ⚡ Performance Improvements

### Chunking Optimization
- **Before**: Token-based (1000 tokens, 200 overlap) - slower but more accurate
- **After**: Character-based (300 chars, 50 overlap) - 3-5x faster with good quality

### LLM Optimization  
- **Model**: Configurable via `GROQ_MODEL` env var (default `qwen/qwen3.8-27b`)
- **Max Tokens**: 1024 (reduced from 2048)
- **Temperature**: 0.3 (more focused responses)

### Database Optimization
- **Batch Processing**: Embeddings in batches of 32
- **Progress Bar**: Disabled for speed
- **ChromaDB**: Optimized operations

## 🔧 Configuration

### Modify Chunking Strategy
Edit `backend/main.py`:
```python
chunker = TextChunker(chunk_size=300, chunk_overlap=50)
```

### Change LLM Model
Set `GROQ_MODEL` in `backend/.env` (default `qwen/qwen3.8-27b`). Check currently supported models with the Groq API, since Groq periodically decommissions models.

### Adjust Database Settings
Edit `backend/embeddings_db.py`:
```python
persist_directory = "../chroma_db"
batch_size = 32
```

## 📝 Usage

1. **Start Backend**: Run `start_backend.bat` or `cd backend && python main.py`
2. **Start Frontend**: Run `start_frontend.bat` or `cd frontend && streamlit run app.py`
3. **Load Documents**: Click "Load All" in the frontend sidebar
4. **Ask Questions**: Type your question and click "Get Answer"

## 🔍 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify dependencies: `cd backend && pip install -r requirements.txt`
- Check `.env` file for API key

### Frontend can't connect
- Ensure backend is running on port 8000
- Check API_BASE_URL in `frontend/app.py`
- Verify firewall settings

### Slow performance
- Reduce chunk size in backend
- Use smaller LLM model
- Clear and reload documents

## 📚 Detailed Documentation

See [README_ARCHITECTURE.md](README_ARCHITECTURE.md) for:
- Detailed architecture explanation
- API usage examples
- Performance optimization guide
- Deployment instructions
- Security considerations

## ☁️ Deployment

This project uses split hosting: the **FastAPI backend** runs on a server host (Render), and the **Streamlit frontend** runs on Streamlit Community Cloud and talks to the backend over HTTPS. Streamlit Cloud cannot host the backend itself, since it only runs the single Streamlit process and has an ephemeral filesystem.

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: University RAG assistant (FastAPI + Streamlit)"
git branch -M main
git remote add origin https://github.com/<your-username>/Uni_Bot.git
git push -u origin main
```

`.env`, `chroma_db/`, `venv/`, and `.streamlit/secrets.toml` are gitignored — secrets never leave your machine or the host dashboards.

### 2. Deploy the backend to Render

The repo includes a `render.yaml` blueprint, so this is a few clicks:

1. On Render, choose **New + → Blueprint** and select the `Uni_Bot` repo.
2. Render reads `render.yaml` and creates the `uni-bot-backend` web service (rootDir `backend`, Python 3.11, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`).
3. In the service **Environment** tab set the secrets the blueprint left blank:
   - `GROQ_API_KEY` — your Groq key
   - `ALLOWED_ORIGINS` — your Streamlit app URL, e.g. `https://<your-app>.streamlit.app` (use `*` only for testing)
4. Deploy. The first boot downloads the embedding model and, because `AUTO_LOAD=true`, builds the vector index from `university_docs/` (~2-3 min). Watch `/load-progress` until `status: done`.
5. Copy the public URL, e.g. `https://uni-bot-backend.onrender.com`.

**Backend environment variables**

| Var | Default | Purpose |
|-----|---------|---------|
| `GROQ_API_KEY` | — | Groq LLM authentication (secret) |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | Chat model; Groq deprecates models over time |
| `DOCS_DIR` | `../university_docs` | PDF source folder (relative to `backend/`) |
| `CHROMA_DIR` | `../chroma_db` | Vector DB location |
| `AUTO_LOAD` | `false` | Rebuild the index on boot when empty (set `true` on ephemeral hosts) |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS allow-list |
| `PORT` | `8000` | Injected automatically by Render |

> Render's free tier disk is ephemeral, so the index is rebuilt on each cold start. For instant starts, attach a persistent disk and point `CHROMA_DIR` at it, then set `AUTO_LOAD=false`.

### 3. Deploy the frontend to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → **Deploy an app** → connect the `Uni_Bot` repo.
2. Set **App file** to `frontend/app.py`.
3. Dependencies come from `requirements.txt` (Streamlit + requests). Theme/config come from `.streamlit/config.toml`.
4. In **App → Settings → Secrets**, add:
   ```toml
   BACKEND_URL = "https://uni-bot-backend.onrender.com"
   ```
   (See `.streamlit/secrets.toml.example`.) The app reads `BACKEND_URL` from secrets or an env var, and falls back to `http://localhost:8000` for local dev.
5. Deploy and open the app. Documents are already indexed by the backend, so you can ask questions immediately.

### Local development

Unset/leave `BACKEND_URL` empty and run both batch files — the frontend defaults to `http://localhost:8000`:

```bash
start_backend.bat    # terminal 1
start_frontend.bat   # terminal 2
```

## 🚧 Future Enhancements

- [ ] Query history and saved questions
- [ ] Multi-turn conversation support
- [ ] Advanced filtering options
- [ ] Export functionality
- [ ] User authentication
- [ ] Mobile app support

## 📝 Requirements

- Python 3.8+
- Groq API key (for LLM features)
- Sufficient disk space for ChromaDB

## 🤝 Contributing

This project is designed for educational and research purposes. The separated architecture makes it easy to extend and customize individual components.

## 📄 License

This project is provided as-is for educational and research purposes.
