@echo off
setlocal
cd /d "%~dp0\backend"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ==================================================
echo  samachar.ai — http://localhost:5000
echo ==================================================
echo.

python server.py
