@echo off
cd /d "%~dp0"

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate

pip install -r requirements.txt

playwright install chromium

python -m streamlit run App.py

pause