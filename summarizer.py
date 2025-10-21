import streamlit as st
from transformers import pipeline
import torch

class Summarizer:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """요약 모델 로드"""
        try:
            # 한국어용 모델 (KoBART)
            st.info("한국어 요약 모델 (KoBART) 로딩 중...")
            self.models['ko'] = pipeline(
                "summarization",
                model="gogamza/kobart-base-v2",
                tokenizer="gogamza/kobart-base-v2",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # 영어용 모델 (BART-large-cnn)
            st.info("영어 요약 모델 (BART-large-cnn) 로딩 중...")
            self.models['en'] = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
        except Exception as e:
            st.error(f"모델 로드 실패: {str(e)}")
    
    def summarize_text(self, text, language='en', max_length=150, min_length=50):
        """텍스트 요약"""
        if not text.strip():
            return "요약할 텍스트가 없습니다."
        
        try:
            # 텍스트가 너무 길면 청크로 나누기
            max_chunk_length = 1000
            if len(text) > max_chunk_length:
                chunks = self.split_text(text, max_chunk_length)
                summaries = []
                
                for chunk in chunks:
                    if chunk.strip():
                        summary = self.models[language](
                            chunk,
                            max_length=max_length,
                            min_length=min_length,
                            do_sample=False
                        )
                        summaries.append(summary[0]['summary_text'])
                
                return " ".join(summaries)
            else:
                summary = self.models[language](
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                return summary[0]['summary_text']
                
        except Exception as e:
            return f"요약 실패: {str(e)}"
    
    def split_text(self, text, max_length):
        """긴 텍스트를 청크로 분할"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
