import streamlit as st
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Tuple, Any
from summarizer import Summarizer
from api_summarizer import APISummarizer

class HybridSummarizer:
    def __init__(self):
        self.local_summarizer = Summarizer()
        self.api_summarizer = APISummarizer()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
    
    def split_into_paragraphs(self, text: str, min_length: int = 200) -> List[str]:
        """텍스트를 문단으로 분할"""
        # 문장 단위로 분할
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        paragraphs = []
        current_paragraph = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > min_length and current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = [sentence]
                current_length = len(sentence)
            else:
                current_paragraph.append(sentence)
                current_length += len(sentence)
        
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        return paragraphs
    
    def generate_embeddings(self, paragraphs: List[str]) -> np.ndarray:
        """문단별 임베딩 생성"""
        try:
            # TF-IDF 벡터화
            tfidf_matrix = self.vectorizer.fit_transform(paragraphs)
            return tfidf_matrix.toarray()
        except Exception as e:
            st.error(f"임베딩 생성 실패: {str(e)}")
            return np.array([])
    
    def find_important_paragraphs(self, paragraphs: List[str], embeddings: np.ndarray, 
                                top_k: int = 5) -> List[Tuple[int, str, float]]:
        """중요한 문단 찾기"""
        if len(paragraphs) == 0 or embeddings.size == 0:
            return []
        
        try:
            # 전체 텍스트의 평균 임베딩 계산
            avg_embedding = np.mean(embeddings, axis=0).reshape(1, -1)
            
            # 각 문단과 평균 임베딩 간의 유사도 계산
            similarities = cosine_similarity(embeddings, avg_embedding).flatten()
            
            # 상위 k개 문단 선택
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            important_paragraphs = []
            for idx in top_indices:
                if idx < len(paragraphs):
                    important_paragraphs.append((idx, paragraphs[idx], similarities[idx]))
            
            return important_paragraphs
            
        except Exception as e:
            st.error(f"중요 문단 찾기 실패: {str(e)}")
            return []
    
    def summarize_paragraphs(self, paragraphs: List[Tuple[int, str, float]], 
                           language: str = "ko", max_length: int = 150) -> List[str]:
        """문단별 요약"""
        summaries = []
        
        for i, (idx, paragraph, score) in enumerate(paragraphs):
            st.info(f"문단 {i+1}/{len(paragraphs)} 요약 중... (중요도: {score:.3f})")
            
            # 문단 요약
            summary = self.local_summarizer.summarize_text(
                paragraph, 
                language=language, 
                max_length=max_length // len(paragraphs),  # 전체 길이를 문단 수로 나눔
                min_length=20
            )
            summaries.append(summary)
        
        return summaries
    
    def create_meta_summary(self, chunk_summaries: List[str], 
                          language: str = "ko", max_length: int = 150) -> str:
        """청크 요약들을 통한 메타 요약 생성"""
        combined_text = " ".join(chunk_summaries)
        
        # 메타 요약 생성
        meta_summary = self.local_summarizer.summarize_text(
            combined_text,
            language=language,
            max_length=max_length,
            min_length=50
        )
        
        return meta_summary
    
    def hybrid_summarize(self, text: str, language: str = "ko", max_length: int = None,
                        use_api: bool = False, api_provider: str = None, api_key: str = None) -> Dict[str, Any]:
        """Hybrid 요약 실행"""
        st.info("🔄 Hybrid 요약 시작...")
        
        # max_length가 None인 경우 기본값 사용
        if max_length is None:
            max_length = 200  # 기본 요약 길이
        
        # 1단계: 문단 분할
        st.info("1️⃣ 문단 분할 중...")
        paragraphs = self.split_into_paragraphs(text)
        st.info(f"총 {len(paragraphs)}개 문단으로 분할됨")
        
        if len(paragraphs) == 0:
            return {"error": "문단을 분할할 수 없습니다."}
        
        # 2단계: 임베딩 생성
        st.info("2️⃣ 임베딩 생성 중...")
        embeddings = self.generate_embeddings(paragraphs)
        
        if embeddings.size == 0:
            return {"error": "임베딩 생성에 실패했습니다."}
        
        # 3단계: 중요한 문단 선택
        st.info("3️⃣ 중요한 문단 선택 중...")
        important_paragraphs = self.find_important_paragraphs(paragraphs, embeddings, top_k=min(5, len(paragraphs)))
        
        if not important_paragraphs:
            return {"error": "중요한 문단을 찾을 수 없습니다."}
        
        st.info(f"상위 {len(important_paragraphs)}개 문단 선택됨")
        
        # 4단계: 문단별 요약
        st.info("4️⃣ 문단별 요약 중...")
        chunk_summaries = self.summarize_paragraphs(important_paragraphs, language, max_length)
        
        # 5단계: 메타 요약 생성
        st.info("5️⃣ 메타 요약 생성 중...")
        meta_summary = self.create_meta_summary(chunk_summaries, language, max_length)
        
        # API 사용 시 추가 요약
        if use_api and api_provider and api_key:
            st.info("6️⃣ API를 통한 최종 요약 중...")
            api_summary = self.api_summarizer.summarize_text(
                meta_summary, 
                api_provider, 
                api_key, 
                language, 
                max_length
            )
            final_summary = api_summary
        else:
            final_summary = meta_summary
        
        return {
            "summary": final_summary,
            "chunk_summaries": chunk_summaries,
            "important_paragraphs": important_paragraphs,
            "paragraph_count": len(paragraphs),
            "selected_count": len(important_paragraphs)
        }
    
    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 특수 문자 제거
        text = re.sub(r'[^\w\s가-힣.,!?]', ' ', text)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 같은 문자 제거
        text = re.sub(r'(.)\1{3,}', r'\1', text)
        return text.strip()
