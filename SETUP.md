# Setup Instructions

## Prerequisites

You need Python installed on your system to run this application. Python is not currently found in your system PATH.

## Installing Python

1. **Download Python**: Visit https://www.python.org/downloads/ and download the latest version (3.8 or higher recommended)

2. **Install Python**:
   - Run the installer
   - **Important**: Check "Add Python to PATH" during installation
   - Complete the installation

3. **Verify Installation**:
   - Open a new terminal/command prompt
   - Run: `python --version` or `py --version`
   - You should see the Python version

## Installing Dependencies

Once Python is installed, navigate to the project directory and run:

```bash
cd "C:\Users\Vishwanth Kondaveeti\Documents\Uni_Bot"
python -m pip install -r requirements.txt
```

Or if using the Python launcher:

```bash
py -m pip install -r requirements.txt
```

## Running the Application

After installing dependencies, run:

```bash
streamlit run app.py
```

Or using Python:

```bash
python -m streamlit run app.py
```

## Alternative: Using Virtual Environment (Recommended)

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Troubleshooting

If you encounter issues:

1. **Python not found**: Make sure you added Python to PATH during installation
2. **Pip not working**: Try `python -m pip` instead of `pip`
3. **Streamlit not found**: Make sure you installed all requirements.txt packages
4. **Memory issues**: If processing large PDFs, consider reducing chunk size in `text_chunker.py`

## Project Files

- `app.py` - Main Streamlit application
- `document_loader.py` - PDF loading and text extraction
- `text_chunker.py` - Text chunking for embeddings
- `embeddings_db.py` - ChromaDB vector database management
- `rag_system.py` - RAG question answering system
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
