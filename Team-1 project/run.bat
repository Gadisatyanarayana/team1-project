@echo off
echo Starting Hindi-Santali Translator...
echo.

REM Use Anaconda Python
set PYTHON_PATH=C:\Users\USER\anaconda3\python.exe

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo Error: Anaconda Python not found at %PYTHON_PATH%
    echo Please install Anaconda or update the path in run.bat
    pause
    exit /b 1
)

REM Install requirements if needed
echo Checking dependencies...
"%PYTHON_PATH%" -m pip install -q Flask Flask-CORS requests python-dotenv gTTS pyttsx3 nltk

echo.
echo Starting Flask application...
echo Access the application at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the application
"%PYTHON_PATH%" main.py

pause
