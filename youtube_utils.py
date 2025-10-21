import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import yt_dlp
import whisper
import os
import tempfile
import re

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
            
            # 다운로드된 파일 찾기
            video_id = info.get('id', 'unknown')
            for file in os.listdir(out_dir):
                if file.startswith(video_id):
                    return os.path.join(out_dir, file)
            
            return None
            
    except Exception as e:
        st.error(f"오디오 다운로드 실패: {str(e)}")
        return None

def transcribe_audio_with_whisper(audio_path):
    """Whisper로 음성 인식"""
    try:
        # Whisper 모델 로드 (base 모델 사용)
        model = whisper.load_model("base")
        
        # 음성 인식
        result = model.transcribe(audio_path, language="ko")
        
        # 텍스트 추출
        text = result["text"]
        
        # 임시 파일 정리
        try:
            os.remove(audio_path)
            if os.path.dirname(audio_path) != os.getcwd():
                os.rmdir(os.path.dirname(audio_path))
        except:
            pass
        
        return text
        
    except Exception as e:
        st.error(f"음성 인식 실패: {str(e)}")
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