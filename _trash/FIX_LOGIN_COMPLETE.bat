@echo off
title Login Fix

echo ========================================
echo  FIXING LOGIN ISSUE
echo ========================================
echo.

echo Step 1: Checking database...
python TEST_DB.py
echo.

echo Step 2: Fixing credentials...
python FIX_LOGIN.py
echo.

echo Step 3: Verifying fix...
python TEST_DB.py
echo.

echo ========================================
echo  DONE!
echo ========================================
echo.
echo Now start the system with START_BOTH.bat
echo.
pause
