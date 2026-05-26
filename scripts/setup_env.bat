@echo off
REM setup_env.bat - create virtual environment and install Python dependencies (Windows CMD)
setlocal
echo [SETUP] Creating virtual environment (if missing)...
python -m venv venv
if ERRORLEVEL 1 (
  echo ERROR: Failed to create venv. Ensure Python is on PATH.
  exit /b 1
)












echo Activating venv and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
if ERRORLEVEL 1 (
  echo ERROR: Some packages failed to install. See output above.
  echo If dlib / face-recognition compilation fails, install CMake and Visual C++ Build Tools and rerun.
  exit /b 1
)

echo.
echo ✅ Setup complete. To activate the venv in a new shell (CMD) run:
echo     venv\Scripts\activate.bat
endlocal
exit /b 0
