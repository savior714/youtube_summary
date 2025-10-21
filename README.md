# 📺 나만의 유튜브 요약 서비스

Lilys AI와 같은 유튜브 요약 서비스의 제약 없이 자유롭게 사용할 수 있는 개인용 요약 서비스입니다.

## ✨ 주요 기능

- 🎯 **자동 자막 추출**: 유튜브 영상의 자막을 자동으로 추출
- 🤖 **AI 요약**: Hugging Face BART 모델을 사용한 고품질 요약
- 🌐 **다국어 지원**: 한국어/영어 자동 감지 및 처리
- ⚙️ **맞춤 설정**: 요약 길이, 언어 등 사용자 설정 가능
- 📱 **간편한 UI**: Streamlit 기반 직관적인 웹 인터페이스
- 📥 **다운로드**: 요약 결과를 텍스트 파일로 저장
- 🎤 **음성 인식**: 자막이 없는 영상은 Whisper로 음성 인식

## 🚀 설치 및 실행

### 1. ffmpeg 설치 (필수)

**Windows 사용자:**
1. [ffmpeg 다운로드](https://www.gyan.dev/ffmpeg/builds/)에서 `ffmpeg-release-essentials.zip` 다운로드
2. `C:\ffmpeg\` 폴더에 압축 해제
3. 최종 경로: `C:\ffmpeg\bin\ffmpeg.exe`

**macOS 사용자:**
```bash
brew install ffmpeg
```

**Linux 사용자:**
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### 2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```

### 4. 브라우저에서 접속
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
- **AI 요약**: Hugging Face Transformers (BART)
- **언어**: Python 3.8+

## 📁 프로젝트 구조

```
youtube/
├── app.py              # Streamlit 메인 애플리케이션
├── youtube_utils.py    # 유튜브 자막 추출 모듈
├── summarizer.py       # AI 요약 모듈
├── requirements.txt    # 의존성 패키지
└── README.md          # 프로젝트 설명서
```

## ⚠️ 주의사항

- 자막이 있는 영상에서만 작동합니다
- 자동 생성 자막도 지원합니다
- 일부 비공개 영상은 접근할 수 없습니다
- GPU가 있으면 더 빠른 처리가 가능합니다
- **ffmpeg 설치 필수**: 자막이 없는 영상의 음성 인식에 필요

## 🐛 문제 해결

### 자막을 찾을 수 없는 경우
- 영상에 자막이 있는지 확인
- 다른 영상으로 시도
- 자동 생성 자막이 있는지 확인

### 요약이 제대로 되지 않는 경우
- 영상 길이가 너무 짧거나 긴 경우
- 자막 품질이 낮은 경우
- 요약 길이 설정을 조정해보세요

### ffmpeg 관련 오류
- `C:\ffmpeg\bin\ffmpeg.exe` 경로에 ffmpeg가 설치되어 있는지 확인
- 시스템 환경변수 PATH에 `C:\ffmpeg\bin` 추가
- 브라우저를 새로고침하여 환경변수 적용

## 📞 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---
*개인용으로 제작된 유튜브 요약 서비스입니다. 상업적 사용 시 관련 라이선스를 확인해주세요.*