# YouTube Summarizer 실행 스크립트 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YouTube Summarizer 시작 중..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 가상환경 활성화
Write-Host "[1/3] 가상환경 확인 중..." -ForegroundColor Yellow

if (Test-Path "venv_new\Scripts\Activate.ps1") {
    Write-Host "가상환경(venv_new) 활성화 중..." -ForegroundColor Green
    & .\venv_new\Scripts\Activate.ps1
} elseif (Test-Path "Scripts\streamlit.exe") {
    Write-Host "프로젝트 루트 환경 사용..." -ForegroundColor Green
} else {
    Write-Host "[오류] 가상환경을 찾을 수 없습니다." -ForegroundColor Red
    $install = Read-Host "패키지를 설치하시겠습니까? (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        Write-Host "패키지 설치 중..." -ForegroundColor Yellow
        pip install -r requirements.txt
    } else {
        Write-Host "설치를 취소했습니다." -ForegroundColor Red
        Read-Host "종료하려면 Enter를 누르세요"
        exit 1
    }
}

Write-Host ""

# 2. 필요한 패키지 확인
Write-Host "[2/3] 필요한 패키지 확인 중..." -ForegroundColor Yellow

try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "streamlit not found"
    }
    Write-Host "모든 패키지가 설치되어 있습니다." -ForegroundColor Green
} catch {
    Write-Host "streamlit이 설치되어 있지 않습니다. 설치 중..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""

# 3. Streamlit 서버 시작
Write-Host "[3/3] Streamlit 서버 시작 중..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "서버가 시작되면 브라우저에서 다음 주소로 접속하세요:" -ForegroundColor Green
Write-Host "http://localhost:8501" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[종료하려면 Ctrl+C를 누르세요]" -ForegroundColor Gray
Write-Host ""

# 프로젝트 루트의 streamlit 사용
if (Test-Path "Scripts\streamlit.exe") {
    & ".\Scripts\streamlit.exe" run app.py
} else {
    streamlit run app.py
}

Read-Host "종료하려면 Enter를 누르세요"

