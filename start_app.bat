@echo off
echo ========================================
echo YouTube Summarizer 시작 중...
echo ========================================
echo.

REM 가상환경 활성화 (venv_new 또는 프로젝트 루트)
if exist "venv_new\Scripts\activate.bat" (
    echo [1/3] 가상환경(venv_new) 활성화 중...
    call venv_new\Scripts\activate.bat
) else if exist "Scripts\streamlit.exe" (
    echo [1/3] 프로젝트 루트 환경 사용...
) else (
    echo [오류] 가상환경을 찾을 수 없습니다.
    echo 패키지를 설치하시겠습니까? (Y/N)
    set /p install_choice=
    if /i "%install_choice%"=="Y" (
        echo 패키지 설치 중...
        pip install -r requirements.txt
    ) else (
        echo 설치를 취소했습니다.
        pause
        exit /b 1
    )
)

echo.
echo [2/3] 필요한 패키지 확인 중...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo streamlit이 설치되어 있지 않습니다. 설치 중...
    pip install -r requirements.txt
)

echo.
echo [3/3] Streamlit 서버 시작 중...
echo.
echo ========================================
echo 서버가 시작되면 브라우저에서 다음 주소로 접속하세요:
echo http://localhost:8501
echo ========================================
echo.
echo [종료하려면 Ctrl+C를 누르세요]
echo.

REM 프로젝트 루트의 streamlit 사용
if exist "Scripts\streamlit.exe" (
    Scripts\streamlit.exe run app.py
) else (
    streamlit run app.py
)

pause

