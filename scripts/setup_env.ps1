# setup_env.ps1 - create virtual environment and install Python dependencies (PowerShell)
Write-Host "[SETUP] Creating virtual environment (if missing)..."
python -m venv venv
if ($LASTEXITCODE -ne 0) {
  Write-Error "Failed to create venv. Ensure Python is available on PATH."
  exit 1
}
Write-Host "Activating venv and installing dependencies..."
& .\venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  Write-Error "Some packages failed to install. If dlib / face-recognition fails, install CMake and Visual C++ Build Tools and rerun."
  exit 1
}
Write-Host "✅ Setup complete. To activate the venv in a new PowerShell session run:`n    .\venv\Scripts\Activate.ps1"