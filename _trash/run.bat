@echo off
echo E-VOTING SYSTEM
echo.
if exist contract_address.txt (
    echo Contract: LOADED
) else (
    echo Contract: NOT LOADED
    echo Run: python load_contract.py YOUR_CONTRACT_ADDRESS
    echo.
    pause
    exit
)
echo.
echo Starting backend...
python app.py
