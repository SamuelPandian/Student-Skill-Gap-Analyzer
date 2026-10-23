@echo off
title NEXUS Launcher
echo ========================================
echo        NEXUS - Starting Services
echo ========================================
echo.

:: Show Database Tables
echo [1/3] Displaying Database Tables...
echo.
cd /d %~dp0backend
python show_database.py
echo.

:: Start Backend
echo [2/3] Starting Backend (FastAPI)...
start "NEXUS Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload"

:: Small delay to let backend start first
timeout /t 3 /nobreak >nul

:: Start Frontend
echo [3/3] Starting Frontend (Vite + React)...
start "NEXUS Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   All services are launching!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ========================================
echo.
echo Close this window anytime. To stop the
echo services, close their individual windows.
pause
