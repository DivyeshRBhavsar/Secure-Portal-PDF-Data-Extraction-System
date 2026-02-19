@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe -m streamlit run App.py
pause