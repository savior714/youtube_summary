# 🤖 Cursor AI 명령어 가이드

이 파일은 Cursor AI가 앱을 쉽게 실행할 수 있도록 도와주는 가이드입니다.

## 📌 빠른 실행 명령어

사용자가 "앱을 실행해 줘" 또는 "서버를 시작해 줘"라고 요청하면 다음 명령어를 실행하세요:

### 방법 1: 간단한 실행 (권장)
```bash
.\run.bat
```

### 방법 2: 직접 실행
```bash
.\Scripts\streamlit.exe run app.py
```

### 방법 3: Python 모듈 실행
```bash
python -m streamlit run app.py
```

### 방법 4: VSCode Task 실행
```bash
# VSCode 명령 팔레트 (Ctrl+Shift+P)에서
Tasks: Run Task → "Run Streamlit App" 선택
```

---

## ⚠️ 중요: 실행 전 체크리스트

### 1. 현재 디렉토리 확인
```bash
pwd
# 또는
cd
```
**반드시** `C:\Users\neo24\Desktop\cursor\youtube` 디렉토리에 있어야 합니다.

### 2. 가상환경 확인 (선택사항)
가상환경 활성화는 **선택사항**입니다. 프로젝트 루트에 이미 패키지가 설치되어 있습니다.

### 3. 패키지 설치 확인
streamlit이 없다는 오류가 발생하면:
```bash
pip install -r requirements.txt
```

---

## 🚀 실행 우선순위

AI는 다음 순서로 실행을 시도해야 합니다:

1. **`.\run.bat`** - 가장 간단하고 안정적
2. **`.\Scripts\streamlit.exe run app.py`** - 프로젝트 루트 환경 사용
3. **`python -m streamlit run app.py`** - Python 모듈로 실행

---

## 📝 실행 결과 확인

명령 실행 후 다음 메시지가 표시되면 성공:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://192.168.0.xxx:8501
```

사용자에게 다음과 같이 알려주세요:
> "Streamlit 서버가 시작되었습니다! 브라우저에서 http://localhost:8501로 접속하세요."

---

## ❌ 오류 처리

### 오류 1: "Could not find platform independent libraries"
**원인:** 가상환경 손상
**해결:** 프로젝트 루트 환경 사용
```bash
.\Scripts\streamlit.exe run app.py
```

### 오류 2: "streamlit 용어가 인식되지 않습니다"
**원인:** 가상환경 미활성화 또는 패키지 미설치
**해결:**
```bash
# 방법 1: 직접 경로 지정
.\Scripts\streamlit.exe run app.py

# 방법 2: 패키지 설치
pip install -r requirements.txt
```

### 오류 3: "ModuleNotFoundError: No module named 'transformers'"
**원인:** 필요한 패키지 미설치
**해결:**
```bash
pip install -r requirements.txt
```

### 오류 4: "git 용어가 인식되지 않습니다"
**원인:** Git이 설치되지 않았거나 PATH에 없음
**해결:** Git 설치 필요 또는 Git Bash 사용

---

## 🎯 AI 행동 규칙

### ✅ DO (해야 할 것)
1. **항상 `.\run.bat`를 먼저 시도**
2. **명령 실행 후 결과 확인**
3. **오류 발생 시 다음 방법 시도**
4. **실행 성공 시 URL 안내**
5. **백그라운드로 실행하지 않고 포그라운드로 실행**

### ❌ DON'T (하지 말아야 할 것)
1. **실행되지도 않았는데 "실행되고 있습니다"라고 말하지 않기**
2. **오류를 무시하지 않기**
3. **가상환경 활성화를 강제하지 않기** (프로젝트 루트 환경 사용 가능)
4. **Git 명령을 PowerShell에서 직접 실행하지 않기** (Git Bash 사용 권장)
5. **백그라운드 실행 시 실제 실행 여부 확인하지 않기**

---

## 💡 사용자 요청 예시

### 요청: "앱을 실행해 줘"
```bash
# AI 실행 명령
.\run.bat
```

### 요청: "서버를 시작해 줘"
```bash
# AI 실행 명령
.\run.bat
```

### 요청: "스트림릿 실행해 줘"
```bash
# AI 실행 명령
.\run.bat
```

### 요청: "로컬 서버 켜줘"
```bash
# AI 실행 명령
.\run.bat
```

---

## 📌 최종 체크리스트

AI가 앱을 실행하기 전에 반드시 확인:

- [ ] 현재 디렉토리가 `C:\Users\neo24\Desktop\cursor\youtube`인가?
- [ ] `run.bat` 파일이 존재하는가?
- [ ] 명령 실행 후 실제로 서버가 시작되었는가?
- [ ] 오류 메시지가 없는가?
- [ ] 사용자에게 올바른 URL을 안내했는가?

**모든 항목이 체크되면 성공!** ✅

