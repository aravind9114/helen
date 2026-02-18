@echo off
REM Interior Design AI - One-Click Launcher

echo =========================================
echo  Starting Interior Design AI System...
echo =========================================

REM Start Backend
cd backend
if exist venv\Scripts\activate (
    echo [Backend] Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo [Warning] venv not found in backend/venv. Trying system python...
)

echo [Backend] Starting server...
start "Backend Server" cmd /k "python main.py"

REM Wait 5 seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend
cd ..\frontend
echo [Frontend] Starting web server...
start "Frontend Server" cmd /k "python -m http.server 8080"

REM Open Browser
echo [Browser] Opening http://localhost:8080...
start http://localhost:8080

echo =========================================
echo  System is running!
echo  Backend: http://localhost:8000
echo  Frontend: http://localhost:8080
echo =========================================
pause
