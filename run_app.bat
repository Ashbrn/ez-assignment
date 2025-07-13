@echo off
echo ========================================
echo Smart Document Assistant - Quick Start
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting application...
echo The app will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py --server.headless true --server.port 8501

pause