@echo off
echo Starting Policy Data Refresh App...
echo.

REM Move to the project directory
cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate

REM Run the Streamlit app
streamlit run App.py

pause