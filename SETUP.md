# YouTube Summarizer - 설정 가이드

## 🚀 빠른 시작

### Windows

1. **간편 실행 (권장)**
   ```bash
   # PowerShell에서
   .\start_app.ps1
   
   # 또는 CMD에서
   start_app.bat
   ```

2. **수동 실행**
   ```bash
   # 1. 가상환경 활성화 (선택사항)
   .\venv_new\Scripts\Activate.ps1
   
   # 2. Streamlit 실행
   streamlit run app.py
   
   # 또는 프로젝트 루트 환경 사용
   .\Scripts\streamlit.exe run app.py
   ```

## 📦 초기 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 가상환경 생성 (선택사항)
```bash
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🔧 문제 해결

### 문제 1: "Could not find platform independent libraries"
**원인:** 가상환경이 손상됨

**해결:**
```bash
# 기존 가상환경 삭제
Remove-Item -Recurse -Force venv_new

# 새로 생성
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 문제 2: "streamlit 용어가 cmdlet으로 인식되지 않습니다"
**원인:** 가상환경이 활성화되지 않음

**해결:**
```bash
# 방법 1: 가상환경 활성화
.\venv_new\Scripts\Activate.ps1
streamlit run app.py

# 방법 2: 직접 경로 지정
.\Scripts\streamlit.exe run app.py

# 방법 3: Python 모듈로 실행
python -m streamlit run app.py
```

### 문제 3: "ModuleNotFoundError: No module named 'transformers'"
**원인:** 필요한 패키지가 설치되지 않음

**해결:**
```bash
pip install -r requirements.txt
```

### 문제 4: Pylance Import 오류 (VSCode)
**원인:** Python 인터프리터 경로가 잘못 설정됨

**해결:**
1. `Ctrl+Shift+P` → "Python: Select Interpreter"
2. `.\Scripts\python.exe` 또는 `.\venv_new\Scripts\python.exe` 선택
3. VSCode 재시작

## 📝 requirements.txt 패키지 목록

```
streamlit>=1.50.0           # 웹 앱 프레임워크
youtube-transcript-api>=1.2.3  # 유튜브 자막 추출
transformers>=4.40.0        # AI 모델
torch>=2.0.0                # 딥러닝 프레임워크
numpy>=1.24.0               # 수치 연산
requests>=2.31.0            # HTTP 요청
```

## 🎯 실행 우선순위

1. **start_app.bat** 또는 **start_app.ps1** 사용 (권장)
   - 자동으로 환경 확인 및 패키지 설치
   - 가장 간편한 방법

2. **프로젝트 루트 환경 사용**
   ```bash
   .\Scripts\streamlit.exe run app.py
   ```
   - 별도 가상환경 불필요
   - 이미 설치된 패키지 사용

3. **가상환경 사용**
   ```bash
   .\venv_new\Scripts\Activate.ps1
   streamlit run app.py
   ```
   - 프로젝트별 독립적인 환경
   - 패키지 충돌 방지

## 🔄 재부팅 후 실행

컴퓨터를 재부팅한 후에는:

1. **가장 간단한 방법**
   ```bash
   .\start_app.bat
   ```
   또는
   ```bash
   .\start_app.ps1
   ```

2. **수동 방법**
   ```bash
   # 프로젝트 폴더로 이동
   cd C:\Users\neo24\Desktop\cursor\youtube
   
   # 실행
   .\Scripts\streamlit.exe run app.py
   ```

## 💡 팁

- **가상환경 없이 사용**: 프로젝트 루트에 이미 패키지가 설치되어 있으므로 `.\Scripts\streamlit.exe run app.py`로 바로 실행 가능
- **자동 실행**: `start_app.bat`을 바탕화면에 바로가기로 만들어두면 더 편리함
- **포트 변경**: 기본 포트(8501)가 사용 중이면 자동으로 8502로 변경됨

## 📌 주의사항

1. **가상환경 손상 시**: 삭제 후 재생성
2. **패키지 업데이트**: `pip install -r requirements.txt --upgrade`
3. **Git 커밋 시**: 가상환경 폴더(venv_new)는 제외됨 (.gitignore에 등록)

