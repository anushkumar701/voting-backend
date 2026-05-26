@echo off
title E-Voting Meets Blockchain — Startup

cls
echo.
echo  ============================================================
echo   E-VOTING MEETS BLOCKCHAIN
echo   Secure   ^|   OTP Auth   ^|   Face Recognition   ^|   Web3
echo  ============================================================
echo.

echo  [1/2] Starting Backend (Flask + Blockchain)...
start "Backend — Flask API" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe app.py"
timeout /t 8 /nobreak >nul
echo         http://localhost:5000  ^|  Ready
echo.

echo  [2/2] Starting Frontend (React)...
start "Frontend — React App" cmd /k "cd /d %~dp0frontend && npm start"
echo         http://localhost:3000  ^|  Compiling...
echo.

echo  ============================================================
echo   SYSTEM STARTING
echo  ============================================================
echo.
echo   Admin    :  admin@admin.com    /  admin123
echo   Officer  :  officer@admin.com  /  officer123
echo   Voter    :  Use OTP Login
echo.
echo   Waiting 30s for React to compile...
timeout /t 30 /nobreak >nul
start http://localhost:3000
echo.
echo   Browser opened. Press any key to close this window.
pause >nul
