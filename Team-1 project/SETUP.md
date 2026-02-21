# Project Setup and Run Instructions

## Quick Start (Recommended)

### Option 1: Double-click to run
1. Simply double-click `run.bat` in Windows Explorer
2. The application will start automatically at http://127.0.0.1:5000

### Option 2: Run from VS Code Terminal
```powershell
.\run.bat
```

OR

```powershell
.\run.ps1
```

## What These Scripts Do

The launcher scripts automatically:
- ✅ Use the correct Python interpreter (Anaconda)
- ✅ Check and install all required dependencies
- ✅ Start the Flask application
- ✅ Show you the URL to access the app

## Manual Setup (If needed)

If the launcher scripts don't work, you can run manually:

```powershell
C:\Users\USER\anaconda3\python.exe -m pip install Flask Flask-CORS requests python-dotenv gTTS pyttsx3 nltk
C:\Users\USER\anaconda3\python.exe main.py
```

## Troubleshooting

### If Anaconda path is different on your system:
1. Find your Anaconda installation path
2. Open `run.bat` or `run.ps1` in a text editor
3. Update the `PYTHON_PATH` variable with your correct path

### Common Anaconda locations:
- `C:\Users\YOUR_USERNAME\anaconda3\python.exe`
- `C:\ProgramData\Anaconda3\python.exe`
- `C:\Anaconda3\python.exe`

## Accessing the Application

Once running, open your web browser and go to:
- Local: http://127.0.0.1:5000
- Or: http://localhost:5000

## Stopping the Application

Press `Ctrl+C` in the terminal where the application is running.
