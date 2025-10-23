# 🎯 프로젝트 템플릿 규칙

모든 프로젝트에서 다음 구조와 파일을 자동으로 생성하여 일관성 있고 사용하기 쉬운 개발 환경을 유지합니다.

---

## 📁 필수 파일 구조

모든 프로젝트는 다음 파일들을 포함해야 합니다:

```
project/
├── run.bat                    # 간단한 실행 스크립트 (AI용)
├── start_app.bat              # 상세한 실행 스크립트 (사용자용)
├── start_app.ps1              # PowerShell 실행 스크립트
├── requirements.txt           # Python 패키지 의존성
├── README.md                  # 프로젝트 설명서
├── SETUP.md                   # 상세 설정 가이드
├── AI_COMMANDS.md            # AI 명령어 가이드
├── .gitignore                # Git 제외 파일
├── .vscode/
│   ├── settings.json         # VSCode 설정
│   └── tasks.json            # VSCode Task 설정
└── [프로젝트 파일들]
```

---

## 📝 1. run.bat (필수)

**목적:** AI가 가장 쉽게 실행할 수 있는 초간단 스크립트

**템플릿:**
```bat
@echo off
REM 간단한 실행 스크립트 - AI가 실행하기 쉬운 버전
cd /d "%~dp0"

REM 여기에 프로젝트별 실행 명령 추가
REM 예시:
REM - Streamlit: Scripts\streamlit.exe run app.py
REM - Flask: python app.py
REM - Django: python manage.py runserver
REM - FastAPI: uvicorn main:app --reload

if exist "Scripts\[실행파일].exe" (
    Scripts\[실행파일].exe [명령어]
) else (
    python [실행명령]
)
```

---

## 📝 2. start_app.bat (권장)

**목적:** 사용자가 직접 실행할 수 있는 상세한 스크립트 (환경 체크, 패키지 설치 등)

**포함 기능:**
- 가상환경 확인 및 활성화
- 필요한 패키지 설치 확인
- 실행 전 환경 체크
- 사용자 친화적인 메시지 출력

---

## 📝 3. AI_COMMANDS.md (필수)

**목적:** AI가 프로젝트를 이해하고 실행하기 위한 가이드

**포함 내용:**
- 빠른 실행 명령어
- 실행 전 체크리스트
- 실행 우선순위
- 오류 처리 방법
- AI 행동 규칙 (DO/DON'T)
- 사용자 요청 예시

**핵심 규칙:**
```markdown
## ⚠️ AI 행동 규칙

### ✅ DO (해야 할 것)
1. **항상 run.bat을 먼저 시도**
2. **명령 실행 후 결과 확인**
3. **오류 발생 시 다음 방법 시도**
4. **실행 성공 시 URL/결과 안내**
5. **실제 실행 여부 확인**

### ❌ DON'T (하지 말아야 할 것)
1. **실행되지도 않았는데 "실행되고 있습니다"라고 말하지 않기**
2. **오류를 무시하지 않기**
3. **백그라운드 실행 시 실제 실행 여부 확인하지 않기**
```

---

## 📝 4. requirements.txt (필수)

**목적:** 패키지 의존성 관리

**작성 규칙:**
- 필수 패키지만 포함
- 버전 범위 지정 (`>=` 사용)
- 너무 엄격한 버전 고정 지양
- 의존성 충돌 최소화

**예시:**
```txt
# 웹 프레임워크
streamlit>=1.50.0
flask>=2.0.0
fastapi>=0.100.0

# 데이터 처리
pandas>=2.0.0
numpy>=1.24.0

# 기타
requests>=2.31.0
```

---

## 📝 5. README.md (필수)

**목적:** 프로젝트 개요 및 빠른 시작 가이드

**구조:**
```markdown
# 프로젝트 이름

[프로젝트 설명 1-2문장]

## ✨ 주요 기능
- 기능 1
- 기능 2
- 기능 3

## 🚀 빠른 시작

### Windows
```bash
# 방법 1: 자동 실행 (권장)
.\start_app.bat

# 방법 2: 간단 실행
.\run.bat

# 방법 3: 수동 실행
pip install -r requirements.txt
[실행 명령어]
```

### 상세 설정
자세한 설정은 [SETUP.md](SETUP.md)를 참고하세요.

## 🐛 문제 해결
### 재부팅 후 실행이 안 되는 경우
```bash
.\run.bat
```

더 자세한 문제 해결은 [SETUP.md](SETUP.md)를 참고하세요.
```

---

## 📝 6. SETUP.md (권장)

**목적:** 상세한 설정 및 문제 해결 가이드

**포함 내용:**
- 초기 설정 방법
- 가상환경 설정
- 문제 해결 방법
- 실행 우선순위
- 포트 설정
- 환경 변수 설정

---

## 📝 7. .vscode/settings.json (권장)

**목적:** VSCode 워크스페이스 설정

**기본 템플릿:**
```json
{
    "git.ignoreLimitWarning": true,
    "python.defaultInterpreterPath": "${workspaceFolder}/Scripts/python.exe",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/Lib/site-packages"
    ],
    "terminal.integrated.cwd": "${workspaceFolder}",
    "files.associations": {
        "*.bat": "bat",
        "*.ps1": "powershell"
    }
}
```

---

## 📝 8. .vscode/tasks.json (권장)

**목적:** VSCode Task 설정 (Ctrl+Shift+P → Run Task)

**기본 템플릿:**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run App",
            "type": "shell",
            "command": "${workspaceFolder}/run.bat",
            "problemMatcher": [],
            "presentation": {
                "reveal": "always",
                "panel": "new",
                "focus": false
            },
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```

---

## 📝 9. .gitignore (필수)

**목적:** Git 제외 파일 설정

**기본 포함 항목:**
```gitignore
# Python
__pycache__/
*.py[cod]
*.so

# Virtual Environment
venv/
venv_new/
ENV/
env/
.venv
Scripts/
Include/
Lib/
pyvenv.cfg

# IDEs
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# 프로젝트별 추가 항목
```

---

## 🎯 AI 실행 프로토콜

### 사용자 요청 시 AI의 행동 순서:

1. **명령어 인식**
   - "앱을 실행해 줘"
   - "서버를 시작해 줘"
   - "프로젝트 실행해 줘"
   - "[프레임워크명] 켜줘"

2. **실행 전 확인**
   - 현재 디렉토리 확인 (`pwd` 또는 `cd`)
   - `run.bat` 파일 존재 확인

3. **실행 시도 (우선순위)**
   ```bash
   # 1순위: run.bat
   .\run.bat
   
   # 2순위: 직접 경로
   .\Scripts\[실행파일].exe [명령어]
   
   # 3순위: Python 모듈
   python -m [모듈명] [명령어]
   ```

4. **결과 확인**
   - 실행 성공 메시지 확인
   - 포트/URL 확인
   - 오류 메시지 확인

5. **사용자 안내**
   - 성공: "서버가 시작되었습니다! [URL]로 접속하세요."
   - 실패: "오류가 발생했습니다. [해결 방법]"

---

## 🚫 AI 금지 행동

### 절대 하지 말아야 할 것:

1. **거짓 보고**
   - ❌ 실행되지 않았는데 "실행되고 있습니다"라고 말하기
   - ✅ 실제 실행 결과를 확인하고 정확히 보고

2. **오류 무시**
   - ❌ 오류 메시지를 보고도 성공했다고 말하기
   - ✅ 오류 발생 시 명확히 알리고 해결 방법 제시

3. **환경 강제**
   - ❌ 가상환경 활성화를 무조건 강요
   - ✅ 프로젝트 루트 환경도 사용 가능함을 인지

4. **백그라운드 실행 오용**
   - ❌ 백그라운드 실행 후 결과 확인 없이 성공 보고
   - ✅ 포그라운드 실행 또는 백그라운드 실행 후 결과 확인

---

## 📋 프로젝트 타입별 실행 명령어

### Streamlit
```bat
if exist "Scripts\streamlit.exe" (
    Scripts\streamlit.exe run app.py
) else (
    python -m streamlit run app.py
)
```

### Flask
```bat
if exist "Scripts\flask.exe" (
    set FLASK_APP=app.py
    Scripts\flask.exe run
) else (
    python app.py
)
```

### Django
```bat
if exist "Scripts\python.exe" (
    Scripts\python.exe manage.py runserver
) else (
    python manage.py runserver
)
```

### FastAPI
```bat
if exist "Scripts\uvicorn.exe" (
    Scripts\uvicorn.exe main:app --reload
) else (
    python -m uvicorn main:app --reload
)
```

### Jupyter Notebook
```bat
if exist "Scripts\jupyter.exe" (
    Scripts\jupyter.exe notebook
) else (
    python -m jupyter notebook
)
```

---

## ✅ 체크리스트

새 프로젝트 시작 시 다음 항목을 확인:

- [ ] `run.bat` 생성 (AI용 간단 실행)
- [ ] `start_app.bat` 또는 `start_app.ps1` 생성 (사용자용 상세 실행)
- [ ] `AI_COMMANDS.md` 생성 (AI 가이드)
- [ ] `requirements.txt` 작성 (의존성 관리)
- [ ] `README.md` 작성 (프로젝트 설명)
- [ ] `SETUP.md` 작성 (상세 가이드)
- [ ] `.gitignore` 설정
- [ ] `.vscode/settings.json` 설정
- [ ] `.vscode/tasks.json` 설정 (선택)

---

## 🎓 핵심 원칙

1. **일관성**: 모든 프로젝트에서 동일한 구조 사용
2. **간결성**: `run.bat` 하나로 실행 가능
3. **명확성**: AI와 사용자 모두 이해하기 쉬운 문서화
4. **신뢰성**: 실행 결과를 항상 검증
5. **유연성**: 다양한 실행 방법 지원

---

**이 템플릿을 따르면 재부팅 후에도 "앱을 실행해 줘" 한 마디로 즉시 실행 가능합니다!** 🚀

