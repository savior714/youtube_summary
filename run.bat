@echo off
REM 간단한 실행 스크립트 - AI가 실행하기 쉬운 버전
cd /d "%~dp0"

if exist "Scripts\streamlit.exe" (
    Scripts\streamlit.exe run app.py
) else (
    python -m streamlit run app.py
)

