# 📺 나만의 유튜브 요약 서비스

Lilys AI와 같은 유튜브 요약 서비스의 제약 없이 자유롭게 사용할 수 있는 개인용 요약 서비스입니다.

## ✨ 주요 기능

- 🎯 **자동 자막 추출**: 유튜브 영상의 자막을 자동으로 추출
- 🚀 **GPU 가속 요약**: CUDA 지원 PyTorch로 빠른 AI 요약
- 🌐 **다국어 지원**: 한국어/영어 자동 감지 및 처리
- ⚙️ **스마트 최적화**: VRAM별 자동 모델 선택 (GTX 1650 4GB 최적화)
- 📱 **간편한 UI**: Streamlit 기반 직관적인 웹 인터페이스
- 📥 **다운로드**: 요약 결과를 텍스트 파일로 저장
- 🎤 **음성 인식**: 자막이 없는 영상은 Whisper로 음성 인식
- 🧠 **청크 처리**: 긴 텍스트도 안정적으로 처리하는 고급 요약 기술

## 🚀 빠른 시작

### 초간단 실행 (권장)

```bash
# 단 한 줄로 실행!
.\run.bat
```

`run.bat` 파일이 자동으로:
- 환경을 확인하고
- 필요한 패키지를 설치하며
- Streamlit 서버를 시작합니다

### 수동 실행

```bash
# 패키지 설치 (최초 1회)
pip install -r requirements.txt

# 실행
streamlit run app.py
```

### 상세 설정 가이드
자세한 설정 및 문제 해결은 [SETUP.md](SETUP.md)를 참고하세요.

### 1. ffmpeg 설치 (선택사항)
자막이 없는 영상의 음성 인식에 필요합니다.

**Windows:**
1. [ffmpeg 다운로드](https://www.gyan.dev/ffmpeg/builds/)
2. `C:\ffmpeg\` 폴더에 압축 해제
3. 최종 경로: `C:\ffmpeg\bin\ffmpeg.exe`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### 2. 브라우저에서 접속
- 자동으로 브라우저가 열리거나
- `http://localhost:8501`로 접속

## 📋 사용법

1. **URL 입력**: 유튜브 영상 URL을 입력창에 붙여넣기
2. **설정 조정**: 사이드바에서 요약 길이, 언어 등 설정
3. **요약 실행**: '요약하기' 버튼 클릭
4. **결과 확인**: 요약 결과 확인 및 다운로드

## 🔧 기술 스택

- **Frontend**: Streamlit
- **자막 추출**: youtube-transcript-api
- **음성 인식**: yt-dlp + Whisper
- **AI 요약**: Transformers (BART) + PyTorch (CUDA 11.8)
- **GPU 가속**: CUDA 지원 PyTorch
- **언어**: Python 3.13

## 📁 프로젝트 구조

```
youtube/
├── app.py                 # Streamlit 메인 애플리케이션
├── youtube_utils.py       # 유튜브 자막 추출 모듈
├── summarizer.py          # AI 요약 모듈 (BART)
├── gpu_utils.py           # GPU 감지 및 최적화 모듈
├── api_summarizer.py      # API 기반 요약 모듈 (미사용)
├── requirements.txt       # 의존성 패키지
├── run.bat               # 초간단 실행 스크립트
└── README.md             # 프로젝트 설명서
```

## 🎯 GPU 최적화

### VRAM별 Whisper 모델 자동 선택
- **VRAM 10GB+**: large-v3 (최고 품질)
- **VRAM 7GB+**: medium
- **VRAM 6GB+**: small
- **VRAM 2-5GB**: base (GTX 1650 4GB 권장)
- **VRAM 1GB**: tiny

### 현재 최적화 상태
- **테스트 환경**: NVIDIA GeForce GTX 1650 (4GB VRAM)
- **사용 모델**: Whisper base + BART
- **CUDA 버전**: 11.8

## 🔮 향후 계획

현재 로컬 GPU(GTX 1650 4GB)의 한계로 인해, 다음과 같은 개선을 계획하고 있습니다:

### 📌 Phase 1: LLM API 통합 (진행 예정)
- **목표**: 추출한 자막을 LLM API(GPT-4, Claude 등)로 전송하여 고품질 요약 생성
- **장점**: 
  - 로컬 GPU 성능 제약 극복
  - 더 정확하고 자연스러운 요약
  - 긴 영상도 안정적으로 처리
- **구현 방식**: 
  - 자막 추출 → 프롬프트 엔지니어링 → LLM API 호출 → 요약 결과 반환
  - 사용자가 API 키를 설정하면 LLM 요약 사용 가능

### 📌 Phase 2: 하이브리드 모드
- 짧은 영상: 로컬 GPU (빠름, 무료)
- 긴 영상/고품질 요약: LLM API (정확함, 유료)

## ⚠️ 주의사항

- 자막이 있는 영상에서만 작동합니다
- 자동 생성 자막도 지원합니다
- 일부 비공개 영상은 접근할 수 없습니다
- **GPU 권장**: CUDA 지원 GPU로 더 빠른 처리 가능
- **ffmpeg 설치 필수**: 자막이 없는 영상의 음성 인식에 필요
- **메모리 요구사항**: 최소 2GB VRAM 권장 (4GB 이상 권장)

## 🐛 문제 해결

### 실행이 안 되는 경우
```bash
# 가장 간단한 방법
.\run.bat
```

### GPU를 인식하지 못하는 경우
PyTorch가 CPU 버전으로 설치되었을 수 있습니다:
```bash
# PyTorch CUDA 버전 재설치
.\venv_new\Scripts\pip.exe uninstall torch torchvision torchaudio -y
.\venv_new\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "Could not find platform independent libraries" 오류
무시해도 됩니다. 앱은 정상 작동합니다.

### "streamlit 용어가 인식되지 않습니다" 오류
```bash
# run.bat 사용 (권장)
.\run.bat

# 또는 직접 경로 지정
.\venv_new\Scripts\streamlit.exe run app.py
```

### "ModuleNotFoundError" 오류
```bash
pip install -r requirements.txt
```

### 자막을 찾을 수 없는 경우
- 영상에 자막이 있는지 확인
- 다른 영상으로 시도
- 자동 생성 자막이 있는지 확인

### 요약이 제대로 되지 않는 경우
- 영상 길이가 너무 짧거나 긴 경우
- 자막 품질이 낮은 경우
- GPU VRAM이 부족한 경우 (CPU 모드로 자동 전환됨)

**더 자세한 문제 해결은 [SETUP.md](SETUP.md)를 참고하세요.**

---

## 📝 최근 업데이트 (2025-10-24)

### ✅ 완료
- ❌ **hybrid_summarizer.py 삭제**: 복잡도 감소 및 유지보수성 향상
- 🚀 **run.bat 간소화**: 한 줄로 실행 가능하도록 개선
- 🎯 **GPU 인식 문제 해결**: PyTorch CUDA 11.8 버전으로 재설치
- 📦 **requirements.txt 최적화**: CUDA 지원 PyTorch 자동 설치 설정

### 🔮 계획 중
- 🤖 **LLM API 통합**: GPT-4/Claude API를 활용한 고품질 요약
- 🔄 **하이브리드 모드**: 로컬 GPU + LLM API 선택 가능

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---
*개인용으로 제작된 유튜브 요약 서비스입니다. 상업적 사용 시 관련 라이선스를 확인해주세요.*