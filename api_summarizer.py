import streamlit as st
import openai
import anthropic
import google.generativeai as genai
import requests
import json
from typing import Optional, Dict, Any

class APISummarizer:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_model = None
    
    def setup_openai(self, api_key: str):
        """OpenAI 클라이언트 설정"""
        try:
            openai.api_key = api_key
            self.openai_client = openai.OpenAI(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"OpenAI 설정 실패: {str(e)}")
            return False
    
    def setup_anthropic(self, api_key: str):
        """Anthropic 클라이언트 설정"""
        try:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"Anthropic 설정 실패: {str(e)}")
            return False
    
    def setup_gemini(self, api_key: str):
        """Google Gemini 클라이언트 설정"""
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            return True
        except Exception as e:
            st.error(f"Gemini 설정 실패: {str(e)}")
            return False
    
    def summarize_with_openai(self, text: str, language: str = "ko", max_length: int = 150) -> str:
        """OpenAI GPT로 요약"""
        if not self.openai_client:
            return "OpenAI 클라이언트가 설정되지 않았습니다."
        
        try:
            language_prompt = "한국어로" if language == "ko" else "in English"
            
            prompt = f"""
다음 텍스트를 {language_prompt}로 요약해주세요. 
요약은 핵심 내용을 간결하게 정리하고, {max_length}자 이내로 작성해주세요.

텍스트:
{text}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 텍스트 요약 전문가입니다. 주어진 텍스트를 정확하고 간결하게 요약합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length * 2,  # 토큰 수는 문자 수의 약 2배
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"OpenAI 요약 실패: {str(e)}"
    
    def summarize_with_anthropic(self, text: str, language: str = "ko", max_length: int = 150) -> str:
        """Anthropic Claude로 요약"""
        if not self.anthropic_client:
            return "Anthropic 클라이언트가 설정되지 않았습니다."
        
        try:
            language_prompt = "한국어로" if language == "ko" else "in English"
            
            prompt = f"""
다음 텍스트를 {language_prompt}로 요약해주세요. 
요약은 핵심 내용을 간결하게 정리하고, {max_length}자 이내로 작성해주세요.

텍스트:
{text}
"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_length * 2,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            return f"Anthropic 요약 실패: {str(e)}"
    
    def summarize_with_gemini(self, text: str, language: str = "ko", max_length: int = 150) -> str:
        """Google Gemini로 요약"""
        if not self.gemini_model:
            return "Gemini 모델이 설정되지 않았습니다."
        
        try:
            language_prompt = "한국어로" if language == "ko" else "in English"
            
            prompt = f"""
다음 텍스트를 {language_prompt}로 요약해주세요. 
요약은 핵심 내용을 간결하게 정리하고, {max_length}자 이내로 작성해주세요.

텍스트:
{text}
"""
            
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Gemini 요약 실패: {str(e)}"
    
    def summarize_text(self, text: str, provider: str, api_key: str, language: str = "ko", max_length: int = None) -> str:
        """API를 사용한 텍스트 요약"""
        if not text.strip():
            return "요약할 텍스트가 없습니다."
        
        # 텍스트 전처리
        text = self.preprocess_text(text)
        st.info(f"전처리된 텍스트 길이: {len(text)}자")
        
        # max_length가 None인 경우 기본값 사용
        if max_length is None:
            max_length = 200  # 기본 요약 길이
        
        # API 제공자별 설정 및 요약
        if provider == "OpenAI (GPT)":
            if not self.openai_client:
                if not self.setup_openai(api_key):
                    return "OpenAI 설정에 실패했습니다."
            return self.summarize_with_openai(text, language, max_length)
        
        elif provider == "Anthropic (Claude)":
            if not self.anthropic_client:
                if not self.setup_anthropic(api_key):
                    return "Anthropic 설정에 실패했습니다."
            return self.summarize_with_anthropic(text, language, max_length)
        
        elif provider == "Google (Gemini)":
            if not self.gemini_model:
                if not self.setup_gemini(api_key):
                    return "Gemini 설정에 실패했습니다."
            return self.summarize_with_gemini(text, language, max_length)
        
        else:
            return f"지원하지 않는 API 제공자: {provider}"
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        import re
        # 특수 문자 제거
        text = re.sub(r'[^\w\s가-힣.,!?]', ' ', text)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 같은 문자 제거 (예: aaaaa -> a)
        text = re.sub(r'(.)\1{3,}', r'\1', text)
        return text.strip()
