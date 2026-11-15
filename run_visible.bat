@echo off
cd /d "%~dp0"
set DEMO_MODE=true
set DATA_DIR=%CD%\backend\data
if not exist .venv\Scripts\python.exe (
  echo Creating project environment...
  py -3 -m venv .venv 2>nul || python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (echo Dependency installation failed. Check internet access and Python 3.10+ & pause & exit /b 1)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
