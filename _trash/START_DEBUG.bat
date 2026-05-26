@echo off
cls
echo ==========================================
echo  COMPLETE FIX + START
echo ==========================================
echo.
echo [1/2] Fixing database...
python DIRECT_FIX.py
echo.
echo [2/2] Starting backend...
echo Check the terminal for login debug info
echo.
python app.py
