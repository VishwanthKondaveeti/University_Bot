@echo off
echo Starting University RAG Backend...
cd /d "%~dp0backend"
if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" main.py
) else (
    echo venv not found - falling back to system Python.
    echo To create it: python -m venv venv ^&^& venv\Scripts\pip install -r backend\requirements.txt -r frontend\requirements.txt
    python main.py
)
