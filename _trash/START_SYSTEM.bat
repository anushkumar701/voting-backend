@echo off
echo ============================================================
echo E-VOTING SYSTEM STARTUP
echo ============================================================
echo.
echo Starting Backend Server...
start "Backend" cmd /k "python app.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo.
echo ============================================================
echo SYSTEM STARTED
echo ============================================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Admin: admin@admin.com / admin123
echo Officer: officer@admin.com / officer123
echo ============================================================
pause
