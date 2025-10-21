import streamlit as st
from transformers import pipeline
import torch

class Summarizer:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """?붿빟 紐⑤뜽 濡쒕뱶"""
        try:
            # ?쒓뎅?댁슜 紐⑤뜽
            self.models['ko'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # ?곸뼱??紐⑤뜽  
            self.models['en'] = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
        except Exception as e:
            st.error(f"紐⑤뜽 濡쒕뱶 ?ㅽ뙣: {str(e)}")
    
    def summarize_text(self, text, language='en', max_length=150, min_length=50):
        """?띿뒪???붿빟"""
        if not text.strip():
            return "?붿빟???띿뒪?멸? ?놁뒿?덈떎."
        
        try:
            # ?띿뒪?멸? ?덈Т 湲몃㈃ 泥?겕濡??섎늻湲?            max_chunk_length = 1000
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
            return f"?붿빟 ?ㅽ뙣: {str(e)}"
    
    def split_text(self, text, max_length):
        """湲??띿뒪?몃? 泥?겕濡?遺꾪븷"""
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
