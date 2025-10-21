import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import whisper
import os
import tempfile
import re

def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_from_api(video_id):
    """YouTube Transcript API로 자막 추출 시도"""
    try:
        # 한국어 자막 우선 시도
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 한국어 자막 찾기
        try:
            transcript = transcript_list.find_transcript(['ko'])
            return transcript.fetch()
        except:
            # 한국어 없으면 영어 자막
            try:
                transcript = transcript_list.find_transcript(['en'])
                return transcript.fetch()
            except:
                # 자동 생성 자막 시도
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                    return transcript.fetch()
                except:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    return transcript.fetch()
    except Exception as e:
        st.warning(f"자막 API 실패: {str(e)}")
        return None

def download_audio_with_ytdlp(url):
    """yt-dlp로 오디오 다운로드"""
    try:
        # 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "audio.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'extractaudio': True,
            'audioformat': 'wav',
            'noplaylist': True,
            'quiet': True,  # 로그 줄이기
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # 다운로드된 파일 찾기
        for file in os.listdir(temp_dir):
            if file.endswith(('.wav', '.mp3', '.m4a', '.webm')):
                return os.path.join(temp_dir, file)
        
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
        
        # 임시 파일 삭제
        try:
            os.remove(audio_path)
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
    transcript_data = get_transcript_from_api(video_id)
    
    if transcript_data:
        st.success("자막 API로 성공!")
        return transcript_data
    
    # 2단계: yt-dlp + Whisper로 음성 인식
    st.info("자막이 없어서 음성 인식으로 시도 중...")
    
    # 오디오 다운로드
    audio_path = download_audio_with_ytdlp(url)
    if not audio_path:
        st.error("오디오 다운로드에 실패했습니다.")
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