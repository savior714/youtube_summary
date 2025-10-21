import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import yt_dlp
import whisper
import os
import tempfile
import re
import glob

def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출 (파라미터 제거)"""
    # &t=516s 같은 파라미터가 붙어도 안전하게 id만 뽑기
    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def fetch_transcript_text(video_id):
    """YouTube Transcript API로 자막 추출 (단순화된 버전)"""
    try:
        # 한국어 우선, 영어 백업
        segs = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        return " ".join(s['text'] for s in segs if s.get('text'))
    except (NoTranscriptFound, TranscriptsDisabled):
        return None
    except Exception as e:
        st.warning(f"자막 API 실패: {str(e)}")
        return None

def download_audio(url, out_dir="tmp", ffmpeg_path=None):
    """yt-dlp로 오디오 다운로드 (ffmpeg 지원)"""
    try:
        os.makedirs(out_dir, exist_ok=True)
        
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
            "noplaylist": True,
            "nocheckcertificate": True,
            "quiet": True,
        }
        
        # ffmpeg 경로가 지정된 경우
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path
        
        # ffmpeg가 있는 경우에만 후처리 추가
        try:
            import subprocess
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        except:
            # ffmpeg가 없으면 원본 포맷 그대로 사용
            pass
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # 다운로드된 파일 찾기 (더 정확한 방법)
            video_id = info.get('id', 'unknown')
            st.info(f"다운로드된 비디오 ID: {video_id}")
            
            # 가능한 파일 확장자들
            possible_extensions = ['mp3', 'wav', 'm4a', 'webm', 'ogg']
            downloaded_file = None
            
            for ext in possible_extensions:
                # 원본 파일 찾기
                original_file = os.path.join(out_dir, f"{video_id}.{ext}")
                if os.path.exists(original_file):
                    downloaded_file = original_file
                    st.info(f"원본 파일 발견: {original_file}")
                    break
                
                # 후처리된 파일 찾기 (ffmpeg가 있는 경우)
                processed_file = os.path.join(out_dir, f"{video_id}.mp3")
                if os.path.exists(processed_file):
                    downloaded_file = processed_file
                    st.info(f"후처리된 파일 발견: {processed_file}")
                    break
            
            # glob으로 모든 파일 검색 (백업 방법)
            if not downloaded_file:
                all_files = glob.glob(os.path.join(out_dir, f"{video_id}.*"))
                if all_files:
                    downloaded_file = all_files[0]
                    st.info(f"Glob으로 파일 발견: {downloaded_file}")
            
            if downloaded_file and os.path.exists(downloaded_file):
                st.success(f"오디오 파일 다운로드 완료: {downloaded_file}")
                return downloaded_file
            else:
                st.error(f"다운로드된 파일을 찾을 수 없습니다. 디렉토리: {out_dir}")
                # 디렉토리 내용 확인
                if os.path.exists(out_dir):
                    files = os.listdir(out_dir)
                    st.error(f"디렉토리 내용: {files}")
                return None
            
    except Exception as e:
        st.error(f"오디오 다운로드 실패: {str(e)}")
        return None

def transcribe_audio_with_whisper(audio_path):
    """Whisper로 음성 인식"""
    try:
        # 절대 경로로 변환
        abs_audio_path = os.path.abspath(audio_path)
        
        # 파일 존재 확인
        if not os.path.exists(abs_audio_path):
            st.error(f"오디오 파일이 존재하지 않습니다: {abs_audio_path}")
            return None
        
        st.info(f"Whisper로 음성 인식 시작: {abs_audio_path}")
        
        # 파일 크기 및 예상 시간 계산
        file_size = os.path.getsize(abs_audio_path)
        file_size_mb = file_size / (1024 * 1024)
        st.info(f"파일 크기: {file_size_mb:.1f}MB ({file_size:,} bytes)")
        
        # 예상 처리 시간 계산 (경험적 공식)
        estimated_minutes = max(1, int(file_size_mb * 0.8))  # 1MB당 약 0.8분
        st.info(f"⏱️ 예상 처리 시간: {estimated_minutes}분 (CPU 사용)")
        
        # 진행률 표시를 위한 컨테이너
        progress_container = st.container()
        with progress_container:
            st.info("🔄 Whisper 모델 로딩 중...")
        
        # ffmpeg 경로 찾기
        ffmpeg_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\ffmpegWbin\\ffmpeg.exe", 
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "ffmpeg"
        ]
        
        ffmpeg_found = None
        for path in ffmpeg_paths:
            try:
                import subprocess
                if path == "ffmpeg":
                    subprocess.run([path, "-version"], capture_output=True, check=True, timeout=5)
                else:
                    subprocess.run([path, "-version"], capture_output=True, check=True, timeout=5)
                ffmpeg_found = path
                st.info(f"ffmpeg 발견: {path}")
                break
            except:
                continue
        
        if not ffmpeg_found:
            st.warning("ffmpeg를 찾을 수 없습니다. 환경변수 PATH를 확인하세요.")
        
        # Whisper 모델 로드 (base 모델 사용)
        with progress_container:
            st.info("🤖 Whisper 모델 로딩 중... (처음 실행 시 다운로드 시간 추가)")
        
        model = whisper.load_model("base")
        
        # 음성 인식 (ffmpeg 경로 지정)
        if ffmpeg_found and ffmpeg_found != "ffmpeg":
            # ffmpeg 경로를 환경변수로 설정
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = os.path.dirname(ffmpeg_found) + os.pathsep + old_path
            st.info(f"ffmpeg 경로 설정: {os.path.dirname(ffmpeg_found)}")
        
        # 음성 인식 시작
        with progress_container:
            st.info("🎤 음성 인식 진행 중... (시간이 오래 걸릴 수 있습니다)")
            
            # 진행률 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 간단한 진행률 시뮬레이션 (실제 Whisper는 진행률을 제공하지 않음)
            import time
            import threading
            
            def update_progress():
                for i in range(10):
                    time.sleep(2)  # 2초마다 업데이트
                    progress_value = (i + 1) * 0.1
                    progress_bar.progress(progress_value)
                    status_text.text(f"음성 인식 진행 중... {int(progress_value * 100)}%")
            
            # 백그라운드에서 진행률 업데이트
            progress_thread = threading.Thread(target=update_progress)
            progress_thread.daemon = True
            progress_thread.start()
        
        # Whisper 옵션 설정 (올바른 매개변수만 사용)
        result = model.transcribe(abs_audio_path, language="ko", verbose=False)
        
        # 텍스트 추출
        text = result["text"]
        
        # 완료 시 진행률 100%로 설정
        with progress_container:
            progress_bar.progress(1.0)
            status_text.text("음성 인식 완료!")
        
        # 성공 메시지
        st.success("✅ 음성 인식 완료!")
        
        # 임시 파일 정리
        try:
            os.remove(abs_audio_path)
            if os.path.dirname(abs_audio_path) != os.getcwd():
                os.rmdir(os.path.dirname(abs_audio_path))
        except:
            pass
        
        return text
        
    except Exception as e:
        st.error(f"음성 인식 실패: {str(e)}")
        st.exception(e)  # 상세한 오류 정보 표시
        return None

def get_transcript(url):
    """자막 추출 (API 우선, 실패시 음성 인식)"""
    video_id = extract_video_id(url)
    if not video_id:
        st.error("유효하지 않은 유튜브 URL입니다.")
        return None
    
    # 1단계: YouTube Transcript API 시도
    st.info("자막 API로 시도 중...")
    text = fetch_transcript_text(video_id)
    
    if text:
        st.success("자막 API로 성공!")
        return [{"text": text, "start": 0, "duration": 0}]
    
    # 2단계: yt-dlp + Whisper로 음성 인식
    st.info("자막이 없어서 음성 인식으로 시도 중...")
    
    # 오디오 다운로드
    audio_path = download_audio(url, out_dir="tmp")
    if not audio_path:
        st.error("오디오 다운로드에 실패했습니다. ffmpeg가 설치되어 있는지 확인하세요.")
        return None
    
    # 음성 인식
    text = transcribe_audio_with_whisper(audio_path)
    if not text:
        st.error("음성 인식에 실패했습니다.")
        return None
    
    st.success("음성 인식으로 성공!")
    
    # Whisper 결과를 API 형식으로 변환
    return [{"text": text, "start": 0, "duration": 0}]

def format_transcript(transcript_data):
    """자막 데이터를 텍스트로 변환"""
    if not transcript_data:
        return ""
    
    text = ""
    for item in transcript_data:
        text += item['text'] + " "
    
    return text.strip()

def detect_language(text):
    """텍스트 언어 감지 (간단한 휴리스틱)"""
    korean_chars = len(re.findall(r'[가-힣]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if korean_chars > english_chars:
        return 'ko'
    else:
        return 'en'