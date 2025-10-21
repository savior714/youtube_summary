import streamlit as st
from transformers import pipeline
import torch
import openai
import os

class Summarizer:
    def __init__(self):
        self.models = {}
        self.openai_client = None
        self.load_models()
    
    def load_models(self):
        """요약 모델 로드"""
        try:
            # OpenAI 클라이언트 초기화
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                st.info("OpenAI API 키가 설정되어 GPT 모델을 사용합니다.")
            else:
                st.warning("OpenAI API 키가 없어서 BART 모델을 사용합니다.")
            
            # BART 모델 (fallback)
            self.models['ko'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.models['en'] = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
        except Exception as e:
            st.error(f"모델 로드 실패: {str(e)}")
    
    def summarize_with_openai(self, text, language='ko', max_length=150):
        """OpenAI GPT로 요약"""
        if not self.openai_client:
            return None
            
        try:
            # 언어별 프롬프트 설정
            if language == 'ko':
                prompt = f"""다음 텍스트를 {max_length}자 이내로 요약해주세요:

{text}

요약:"""
            else:
                prompt = f"""Please summarize the following text in {max_length} characters or less:

{text}

Summary:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning(f"OpenAI 요약 실패: {str(e)}")
            return None
    
    def summarize_text(self, text, language='ko', max_length=150, min_length=50):
        """텍스트 요약"""
        if not text.strip():
            return "요약할 텍스트가 없습니다."
        
        # OpenAI GPT 시도
        if self.openai_client:
            st.info("OpenAI GPT로 요약 중...")
            summary = self.summarize_with_openai(text, language, max_length)
            if summary:
                return summary
        
        # BART 모델 fallback
        st.info("BART 모델로 요약 중...")
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