# 📺 나만의 유튜브 요약 서비스

Lilys AI와 같은 유튜브 요약 서비스의 제약 없이 자유롭게 사용할 수 있는 개인용 요약 서비스입니다.

## ✨ 주요 기능

- 🎯 **자동 자막 추출**: 유튜브 영상의 자막을 자동으로 추출
- 🚀 **LongT5 적응형 AI**: GPU VRAM에 따른 자동 최적화된 요약 시스템
- 🌐 **다국어 지원**: 한국어/영어 자동 감지 및 처리
- ⚙️ **스마트 최적화**: VRAM별 자동 모델 선택 (Full Precision/8bit/4bit)
- 📱 **간편한 UI**: Streamlit 기반 직관적인 웹 인터페이스
- 📥 **다운로드**: 요약 결과를 텍스트 파일로 저장
- 🎤 **음성 인식**: 자막이 없는 영상은 Whisper로 음성 인식
- 🧠 **청크 처리**: 긴 텍스트도 안정적으로 처리하는 고급 요약 기술

## 🚀 설치 및 실행

### 빠른 시작 (Windows)

**방법 1: 자동 실행 스크립트 (권장)**
```bash
# PowerShell
.\start_app.ps1

# 또는 CMD
start_app.bat
```

**방법 2: 수동 실행**
```bash
# 패키지 설치
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
- **AI 요약**: LongT5 (google/long-t5-tglobal-base) + BART fallback
- **최적화**: bitsandbytes (양자화), accelerate (분산 처리)
- **언어**: Python 3.8+

## 📁 프로젝트 구조

```
youtube/
├── app.py                 # Streamlit 메인 애플리케이션
├── youtube_utils.py       # 유튜브 자막 추출 모듈
├── summarizer.py          # LongT5 적응형 AI 요약 모듈
├── gpu_utils.py           # GPU 감지 및 최적화 모듈
├── api_summarizer.py      # API 기반 요약 모듈
├── hybrid_summarizer.py   # 하이브리드 요약 모듈
├── requirements.txt       # 의존성 패키지
└── README.md             # 프로젝트 설명서
```

## 🚀 LongT5 적응형 시스템

### VRAM별 자동 최적화
- **VRAM 12GB+**: Full Precision 모드 (청크 8K, 토큰 800)
- **VRAM 8GB+**: 8bit 양자화 (청크 4K, 토큰 600)  
- **VRAM 4GB+**: 8bit 양자화 (청크 2.5K, 토큰 400)
- **VRAM 2GB+**: 4bit 양자화 (청크 1.8K, 토큰 300)
- **CPU**: BART 모델 fallback

### 🧠 고급 기능
- **청크 기반 처리**: 긴 텍스트를 안전하게 분할하여 처리
- **메모리 효율성**: 양자화를 통한 VRAM 절약
- **자동 fallback**: LongT5 실패 시 BART 모델로 자동 전환
- **프롬프트 최적화**: 언어별 맞춤형 요약 지시

## ⚠️ 주의사항

- 자막이 있는 영상에서만 작동합니다
- 자동 생성 자막도 지원합니다
- 일부 비공개 영상은 접근할 수 없습니다
- **GPU 권장**: LongT5 적응형 시스템으로 더 빠른 처리 가능
- **ffmpeg 설치 필수**: 자막이 없는 영상의 음성 인식에 필요
- **메모리 요구사항**: 최소 2GB VRAM 권장 (4GB 이상 권장)

## 🐛 문제 해결

### 재부팅 후 실행이 안 되는 경우
```bash
# 가장 간단한 방법
.\start_app.bat

# 또는
.\start_app.ps1
```

### "Could not find platform independent libraries" 오류
가상환경이 손상된 경우입니다. 프로젝트 루트 환경을 사용하세요:
```bash
.\Scripts\streamlit.exe run app.py
```

### "streamlit 용어가 인식되지 않습니다" 오류
```bash
# 방법 1: 직접 경로 지정
.\Scripts\streamlit.exe run app.py

# 방법 2: Python 모듈로 실행
python -m streamlit run app.py
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
- LongT5 모델 로딩 실패 시 BART 모델로 자동 fallback

**더 자세한 문제 해결은 [SETUP.md](SETUP.md)를 참고하세요.**

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---
*개인용으로 제작된 유튜브 요약 서비스입니다. 상업적 사용 시 관련 라이선스를 확인해주세요.*