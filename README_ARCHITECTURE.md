# Vignan University Knowledge Assistant - Frontend/Backend Architecture

## 🏗️ Project Structure

```
Uni_Bot/
├── backend/                    # FastAPI Backend Server
│   ├── main.py                # FastAPI application with API endpoints
│   ├── document_loader.py     # PDF document loading and processing
│   ├── text_chunker.py        # Optimized text chunking
│   ├── embeddings_db.py       # ChromaDB vector database management
│   ├── rag_system.py          # RAG system with LLM integration
│   ├── requirements.txt       # Backend dependencies
│   └── .env                   # Environment variables (API keys)
├── frontend/                   # Streamlit Frontend Application
│   ├── app.py                 # Streamlit UI
│   └── requirements.txt       # Frontend dependencies
├── university_docs/            # Document storage
│   ├── policies/             # Policy PDFs
│   ├── regulations/          # Regulation PDFs
│   └── *.pdf                 # Additional documents
├── chroma_db/                 # Vector database storage (auto-created)
├── start_backend.bat          # Windows script to start backend
├── start_frontend.bat         # Windows script to start frontend
└── .env                       # Root environment variables
```

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

**Option 1: Using Batch Files (Windows)**
```bash
# Terminal 1: Start Backend
start_backend.bat

# Terminal 2: Start Frontend
start_frontend.bat
```

**Option 2: Manual Start**
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

## 🔧 Architecture Overview

### Backend (FastAPI)

The backend handles all heavy processing and provides REST API endpoints:

**Key Components:**
- **Document Processing**: Loads PDFs from `university_docs/` folder
- **Optimized Chunking**: Character-based chunking (300 chars, 50 overlap) for speed
- **Vector Database**: ChromaDB with Sentence Transformers embeddings
- **LLM Integration**: Groq API with Llama3-8b for fast, intelligent responses
- **REST API**: Clean endpoints for frontend communication

**API Endpoints:**
- `GET /` - Health check
- `GET /status` - Get current system status
- `POST /load-documents` - Load and process documents (background task)
- `POST /query` - Query the knowledge base
- `POST /clear-documents` - Clear all documents

### Frontend (Streamlit)

The frontend provides a user-friendly interface:

**Features:**
- Modern gradient UI design
- Real-time status updates from backend
- Document category display
- Interactive Q&A interface
- Source attribution with categories
- Error handling and user feedback

## ⚡ Performance Optimizations

### Chunking Speed Improvements

**Before:** Token-based chunking (1000 tokens, 200 overlap)
- Used tiktoken for tokenization
- Slower processing due to token counting
- Better for accuracy but slower

**After:** Character-based chunking (300 chars, 50 overlap)
- Direct string manipulation
- 3-5x faster processing
- Optimized for speed while maintaining quality
- Sentence boundary detection for better chunks

### Database Optimizations

**Batch Processing:**
- Embeddings generated in batches of 32
- Progress bar disabled for speed
- Optimized ChromaDB operations

**LLM Optimizations:**
- Switched from Llama3-70b to Llama3-8b
- Reduced max_tokens from 2048 to 1024
- Lower temperature (0.3) for faster, focused responses
- Maintained answer quality while improving speed

## 📡 API Usage Examples

### Check Status
```bash
curl http://localhost:8000/status
```

### Load Documents
```bash
curl -X POST http://localhost:8000/load-documents
```

### Query Knowledge Base
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the attendance requirement?", "top_k": 5}'
```

### Clear Documents
```bash
curl -X POST http://localhost:8000/clear-documents
```

## 🔍 Troubleshooting

### Backend Issues

**Backend won't start:**
- Check if port 8000 is available
- Verify all dependencies are installed
- Check `.env` file for API key

**Document loading fails:**
- Verify `university_docs/` folder exists
- Check PDF files are not corrupted
- Ensure sufficient disk space

### Frontend Issues

**Can't connect to backend:**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in frontend/app.py

**Slow performance:**
- Reduce chunk size in backend/main.py
- Use smaller LLM model
- Clear and reload documents

## 🎯 Benefits of New Architecture

### Separation of Concerns
- **Backend**: Handles all processing, database operations, and AI
- **Frontend**: Focuses on user interface and experience
- **API**: Clean communication layer between components

### Scalability
- Backend can be deployed independently
- Multiple frontends can connect to same backend
- Easy to add new API endpoints

### Performance
- Optimized chunking reduces processing time
- Background tasks prevent UI blocking
- Efficient database operations

### Maintainability
- Clear code organization
- Easy to update individual components
- Better error handling and debugging

## 📝 Development Notes

### Adding New Features

**To add a new API endpoint:**
1. Add endpoint function in `backend/main.py`
2. Update frontend to call new endpoint
3. Add error handling in both components

**To modify chunking strategy:**
1. Update `TextChunker` in `backend/text_chunker.py`
2. Adjust parameters in `backend/main.py`
3. Test with sample documents

**To change LLM model:**
1. Update model name in `backend/rag_system.py`
2. Adjust parameters as needed
3. Test response quality and speed

## 🔐 Security Considerations

- API keys stored in `.env` files (never commit to git)
- CORS enabled for development (restrict in production)
- Input validation on API endpoints
- Error messages don't expose sensitive information

## 🚀 Deployment

### Backend Deployment
- Deploy to cloud platform (AWS, GCP, Azure)
- Use environment variables for configuration
- Scale horizontally if needed
- Consider containerization (Docker)

### Frontend Deployment
- Deploy to Streamlit Cloud or similar
- Update API_BASE_URL for production
- Configure authentication if needed
- Enable HTTPS for secure communication

## 📊 Monitoring

### Backend Health
- Monitor API response times
- Track database size and performance
- Log errors and warnings
- Monitor LLM API usage

### Frontend Performance
- Track user interactions
- Monitor API call success rates
- Collect user feedback
- Analyze query patterns

## 🎓 Next Steps

1. **Testing**: Test with various document types and queries
2. **Optimization**: Further optimize based on usage patterns
3. **Features**: Add advanced features like query history
4. **Deployment**: Deploy to production environment
5. **Monitoring**: Set up monitoring and alerting

---

**Built with FastAPI, Streamlit, ChromaDB, and Groq LLM**
