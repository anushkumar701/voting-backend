@echo off
cls
echo ==========================================
echo  COMPLETE STARTUP
echo ==========================================
echo.
echo [1/3] Creating fresh database...
python CREATE_FRESH_DB.py
echo.
echo [2/3] Starting backend...
start "Backend" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo.
echo [3/3] Starting frontend...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..
echo.
echo ==========================================
echo  SYSTEM STARTED
echo ==========================================
echo.
echo Login: admin@admin.com / admin123
echo.
pause
