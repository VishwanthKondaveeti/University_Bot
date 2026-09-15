@echo off
echo Starting University RAG Frontend...
cd /d "%~dp0frontend"
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m streamlit run app.py
) else (
    echo venv not found - falling back to system Streamlit.
    echo To create it: python -m venv venv ^&^& venv\Scripts\pip install -r backend\requirements.txt -r frontend\requirements.txt
    streamlit run app.py
)
