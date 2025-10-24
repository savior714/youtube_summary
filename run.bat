@echo off
setlocal

REM 한글 깨짐 방지를 위해 코드 페이지를 UTF-8로 변경
chcp 65001 > nul

REM 스크립트가 있는 디렉토리로 이동 (안정적인 실행을 위해)
cd /d "%~dp0"

echo ======================================================
echo  YouTube Summarizer 앱을 시작합니다.
echo ======================================================
echo.

echo [1/2] 실행 환경을 확인합니다...

set "PYTHON_EXE="

REM 방법 1: 프로젝트 루트의 python.exe 사용 (가장 안정적이고 권장되는 방식)
if exist ".\Scripts\python.exe" (
    echo  -^> [성공] 프로젝트의 Python 환경을 찾았습니다.
    set "PYTHON_EXE=.\Scripts\python.exe"
)

REM 방법 2: 'venv_new' 폴더의 python.exe 사용 (차선책)
if not defined PYTHON_EXE if exist ".\venv_new\Scripts\python.exe" (
    echo  -^> [성공] 'venv_new' 가상환경을 찾았습니다.
    set "PYTHON_EXE=.\venv_new\Scripts\python.exe"
)

REM 방법 3: 시스템에 설치된 Python 사용 (최후의 수단)
if not defined PYTHON_EXE (
    echo  -^> [정보] 시스템에 설치된 Python을 사용합니다.
    set "PYTHON_EXE=python"
)

echo.
echo [2/4] 패키지 관리자(pip)를 최신 버전으로 업데이트합니다...

"%PYTHON_EXE%" -m pip install --upgrade pip

echo.
echo [3/4] 필요한 패키지를 확인하고 설치합니다...

REM requirements.txt 파일이 있는지 확인
if not exist "requirements.txt" (
    echo [오류] requirements.txt 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

REM pip를 사용하여 패키지 설치
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다. 위의 오류 메시지를 확인하세요.
    pause
    exit /b 1
)

echo.
echo [4/4] Streamlit 서버를 시작합니다...
echo.
"%PYTHON_EXE%" -m streamlit run app.py

:end
echo.
echo 스크립트가 종료되었습니다. 오류가 발생했다면 위의 메시지를 확인하세요.
pause