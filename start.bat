@echo off
echo ==========================================
echo Wedding Invitation App - Setup and Run
echo ==========================================

echo Installing dependencies...
pip install -r backend\requirements.txt

echo Generating dummy template and downloading font...
python generate_dummy.py

echo Starting the Web Server (Backend)...
echo IMPORTANT: Open frontend\index.html in your web browser!
echo.
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
