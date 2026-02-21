# Hindi-Santali Translator Launcher Script
Write-Host "Starting Hindi-Santali Translator..." -ForegroundColor Green
Write-Host ""

# Use Anaconda Python
$PYTHON_PATH = "C:\Users\USER\anaconda3\python.exe"

# Check if Python exists
if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "Error: Anaconda Python not found at $PYTHON_PATH" -ForegroundColor Red
    Write-Host "Please install Anaconda or update the path in run.ps1" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install requirements if needed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
& $PYTHON_PATH -m pip install -q Flask Flask-CORS requests python-dotenv gTTS pyttsx3 nltk

Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "Access the application at: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the application
& $PYTHON_PATH main.py
