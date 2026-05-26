@echo off
echo Fixing login and starting backend...
python FIX_LOGIN.py
echo.
python app.py
