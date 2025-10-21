import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

def extract_video_id(url):
    """?좏뒠釉?URL?먯꽌 鍮꾨뵒??ID 異붿텧"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """?좏뒠釉??먮쭑 異붿텧"""
    try:
        # ?쒓뎅???먮쭑 ?곗꽑 ?쒕룄
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # ?쒓뎅???먮쭑 李얘린
        try:
            transcript = transcript_list.find_transcript(['ko'])
            return transcript.fetch()
        except:
            # ?쒓뎅???놁쑝硫??곸뼱 ?먮쭑
            try:
                transcript = transcript_list.find_transcript(['en'])
                return transcript.fetch()
            except:
                # ?먮룞 ?앹꽦 ?먮쭑 ?쒕룄
                try:
                    transcript = transcript_list.find_generated_transcript(['ko'])
                    return transcript.fetch()
                except:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    return transcript.fetch()
    except Exception as e:
        st.error(f"?먮쭑 異붿텧 ?ㅽ뙣: {str(e)}")
        return None

def format_transcript(transcript_data):
    """?먮쭑 ?곗씠?곕? ?띿뒪?몃줈 蹂??""
    if not transcript_data:
        return ""
    
    text = ""
    for item in transcript_data:
        text += item['text'] + " "
    
    return text.strip()

def detect_language(text):
    """?띿뒪???몄뼱 媛먯? (媛꾨떒???대━?ㅽ떛)"""
    korean_chars = len(re.findall(r'[媛-??', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if korean_chars > english_chars:
        return 'ko'
    else:
        return 'en'
