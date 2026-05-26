@echo off
echo Deleting documentation files...

del /Q *.txt 2>nul
del /Q *.md 2>nul
del /Q *FIX*.py 2>nul
del /Q *LOGIN*.py 2>nul
del /Q *TEST*.py 2>nul
del /Q *COMPLETE*.bat 2>nul
del /Q START.bat 2>nul
del /Q CLEANUP.bat 2>nul
del /Q RUN_FIX.bat 2>nul

echo Keeping only:
echo   FIX_NOW.py
echo   FIX.bat
echo   START_BOTH.bat
echo   START_BACKEND.bat
echo   START_FRONTEND.bat
echo.
pause
