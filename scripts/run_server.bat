@echo off
REM run_server.bat - run backend using project venv (Windows CMD)
if not exist venv (
  echo Virtual environment not found. Run scripts\setup_env.bat first.
  exit /b 1
)
call venv\Scripts\activate.bat
python app.py
