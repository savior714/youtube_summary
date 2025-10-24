@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ======================================================
echo  YouTube Summarizer - Starting Streamlit App
echo ======================================================
echo.

echo [1/2] Checking environment...

REM Check if Scripts\streamlit.exe exists
if exist ".\Scripts\streamlit.exe" (
    echo  [OK] Found Streamlit in project Scripts folder
    echo.
    echo [2/2] Starting Streamlit server...
    echo.
    ".\Scripts\streamlit.exe" run app.py
    goto :end
)

REM Check if venv_new\Scripts\streamlit.exe exists
if exist ".\venv_new\Scripts\streamlit.exe" (
    echo  [OK] Found Streamlit in venv_new folder
    echo.
    echo [2/2] Starting Streamlit server...
    echo.
    ".\venv_new\Scripts\streamlit.exe" run app.py
    goto :end
)

REM Fallback to system Python
echo  [INFO] Using system Python/Streamlit
echo.
echo [2/2] Starting Streamlit server...
echo.
python -m streamlit run app.py

:end
echo.
echo Script finished. Check above for any errors.
pause