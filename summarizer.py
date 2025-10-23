import streamlit as st
from transformers import pipeline
import torch
import re
from gpu_utils import GPUDetector

class Summarizer:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """LongT5 적응형 모델 로드 (VRAM에 따라 최적화)"""
        try:
            # GPU 정보 확인
            detector = GPUDetector()
            device_info = detector.get_device_info()
            
            vram_gb = device_info["vram_gb"]
            device = device_info["device"]
            gpu_name = device_info["gpu_name"]
            
            st.info(f"🔍 GPU: {gpu_name} ({vram_gb} GB VRAM)")
            
            # VRAM별 LongT5 로딩 정책
            if vram_gb >= 12:
                load_kwargs = {"device_map": "auto"}  # full precision
                chunk_size = 8000
                max_new_tokens = 800
                st.info("🚀 고성능 GPU 감지 - Full Precision 모드")
            elif vram_gb >= 8:
                load_kwargs = {"device_map": "auto", "load_in_8bit": True}
                chunk_size = 4000
                max_new_tokens = 600
                st.info("⚡ 중고성능 GPU 감지 - 8bit 양자화 모드")
            elif vram_gb >= 4:
                load_kwargs = {"device_map": "auto", "load_in_8bit": True}
                chunk_size = 2500
                max_new_tokens = 400
                st.info("🔧 보급형 GPU 감지 - 8bit 양자화 모드")
            elif vram_gb >= 2:
                load_kwargs = {"device_map": "auto", "load_in_4bit": True}
                chunk_size = 1800
                max_new_tokens = 300
                st.info("💾 저사양 GPU 감지 - 4bit 양자화 모드")
            else:
                # CPU fallback
                load_kwargs = {"device_map": "cpu"}
                chunk_size = 1200
                max_new_tokens = 200
                st.info("🖥️ CPU 모드 - 최소 설정")
            
            st.info(f"🧠 설정: chunk_size={chunk_size}, max_new_tokens={max_new_tokens}")
            
            # LongT5 모델 로드
            st.info("🔄 LongT5 모델 로딩 중...")
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            model_name = "google/long-t5-tglobal-base"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **load_kwargs)
            model.eval()
            
            # 설정 저장
            self.longt5_model = model
            self.longt5_tokenizer = tokenizer
            self.device = device
            self.chunk_size = chunk_size
            self.max_new_tokens = max_new_tokens
            
            st.success("✅ LongT5 적응형 모델 로드 완료!")
            
        except Exception as e:
            st.error(f"LongT5 모델 로드 실패: {str(e)}")
            st.info("🔄 BART 모델로 fallback...")
            # Fallback to BART models
            self._load_fallback_models()
    
    def _load_fallback_models(self):
        """BART 모델 fallback 로딩"""
        try:
            # 한국어용 모델 (KoBART)
            st.info("한국어 요약 모델 (KoBART) 로딩 중...")
            self.models['ko'] = pipeline(
                "summarization",
                model="gogamza/kobart-base-v2",
                tokenizer="gogamza/kobart-base-v2",
                device=-1,
                max_length=None
            )
            
            # 영어용 모델 (BART-large-cnn)
            st.info("영어 요약 모델 (BART-large-cnn) 로딩 중...")
            self.models['en'] = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                tokenizer="facebook/bart-large-cnn",
                device=-1,
                max_length=None
            )
            
            # LongT5 사용 불가 플래그 설정
            self.longt5_model = None
            self.longt5_tokenizer = None
            
        except Exception as e:
            st.error(f"Fallback 모델 로드 실패: {str(e)}")
    
    def summarize_text(self, text, language='en', max_length=None, min_length=None):
        """LongT5 적응형 텍스트 요약"""
        if not text.strip():
            return "요약할 텍스트가 없습니다."
        
        try:
            # 텍스트 전처리
            text = self.preprocess_text(text)
            st.info(f"전처리된 텍스트 길이: {len(text)}자")
            
            # LongT5 사용 가능한지 확인
            if hasattr(self, 'longt5_model') and self.longt5_model is not None:
                st.info("🚀 LongT5 적응형 요약 시작...")
                return self._summarize_with_longt5(text, language)
            else:
                st.info("🔄 BART 모델로 요약...")
                return self._summarize_with_bart(text, language)
                
        except Exception as e:
            st.error(f"요약 실패: {str(e)}")
            return f"요약 실패: {str(e)}"
    
    def _summarize_with_longt5(self, text, language):
        """LongT5 적응형 요약"""
        import torch
        
        # 프롬프트 설정
        if language == 'ko':
            prompt_prefix = "다음 텍스트를 상세하고 체계적으로 요약해주세요. 주요 내용을 구체적으로 설명하고, 중요한 세부사항을 포함해주세요:\n\n"
        else:
            prompt_prefix = "Please provide a detailed and comprehensive summary of the following text. Include specific details and key points:\n\n"
        
        # 텍스트를 청크로 분할
        chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        st.info(f"📊 총 {len(chunks)}개 청크로 분할됨 (청크 크기: {self.chunk_size}자)")
        
        chunk_summaries = []
        progress_text = st.empty()
        
        # 각 청크 요약
        for i, chunk in enumerate(chunks):
            progress_text.info(f"🔄 청크 요약 진행 중: {i+1}/{len(chunks)}")
            
            try:
                # 프롬프트와 청크 결합
                prompt_text = prompt_prefix + chunk
                
                # 토크나이징
                inputs = self.longt5_tokenizer(
                    prompt_text, 
                    return_tensors="pt", 
                    truncation=True, 
                    max_length=4096
                ).to(self.device)
                
                # 요약 생성 (일관성을 위해 deterministic 설정)
                with torch.no_grad():
                    output = self.longt5_model.generate(
                        **inputs,
                        max_new_tokens=self.max_new_tokens,
                        no_repeat_ngram_size=3,
                        num_beams=4,  # 빔 서치로 더 안정적인 결과
                        early_stopping=True,
                        do_sample=False,  # 샘플링 비활성화로 일관성 확보
                        temperature=1.0  # do_sample=False일 때는 무시됨
                    )
                
                # 결과 디코딩
                summary = self.longt5_tokenizer.decode(output[0], skip_special_tokens=True)
                chunk_summaries.append(summary)
                
                # VRAM 정리
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                st.warning(f"청크 {i+1} 요약 실패: {str(e)}")
                # 실패시 원본 청크의 일부를 요약으로 사용
                fallback_summary = chunk[:200] + "..." if len(chunk) > 200 else chunk
                chunk_summaries.append(fallback_summary)
        
        progress_text.success(f"✅ 청크 요약 완료: {len(chunk_summaries)}개 청크 처리됨")
        
        # 최종 요약 생성
        if len(chunk_summaries) > 1:
            st.info("🔄 최종 요약 생성 중...")
            combined_summaries = " ".join(chunk_summaries)
            
            try:
                # 최종 요약 프롬프트
                if language == 'ko':
                    final_prompt = f"다음 내용들을 종합하여 체계적이고 상세한 최종 요약을 작성해주세요. 주요 내용을 구체적으로 설명하고, 중요한 세부사항을 모두 포함해주세요:\n\n{combined_summaries}"
                else:
                    final_prompt = f"Please create a comprehensive and detailed final summary by synthesizing the following content. Include all key points and specific details:\n\n{combined_summaries}"
                
                final_inputs = self.longt5_tokenizer(
                    final_prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=4096
                ).to(self.device)
                
                final_output = self.longt5_model.generate(
                    **final_inputs,
                    max_new_tokens=self.max_new_tokens,
                    no_repeat_ngram_size=3,
                    num_beams=4,  # 빔 서치로 더 안정적인 결과
                    early_stopping=True,
                    do_sample=False,  # 샘플링 비활성화로 일관성 확보
                    temperature=1.0  # do_sample=False일 때는 무시됨
                )
                
                final_summary = self.longt5_tokenizer.decode(final_output[0], skip_special_tokens=True)
                
                # VRAM 정리
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                
                return self._postprocess_summary(final_summary, language)
                
            except Exception as e:
                st.warning(f"최종 요약 실패, 청크 요약 결합: {str(e)}")
                return self._postprocess_summary(combined_summaries, language)
        else:
            return self._postprocess_summary(chunk_summaries[0], language)
    
    def _summarize_with_bart(self, text, language):
        """BART 모델 fallback 요약"""
        # 기존 BART 로직 사용
        if len(text) > 2000:
            st.info("🔄 긴 텍스트 감지 - 청크 단위로 요약 중...")
            summary = self._summarize_long_text(text, language)
        else:
            st.info("🔄 전체 텍스트 요약 중...")
            summary = self._summarize_short_text(text, language)
        
        return self._postprocess_summary(summary, language)
    
    def _summarize_short_text(self, text, language):
        """짧은 텍스트 요약"""
        # 프롬프트 기반 요약을 위한 텍스트 전처리
        if language == 'ko':
            prompt_text = f"다음 텍스트를 상세하고 체계적으로 요약해주세요. 주요 내용을 구체적으로 설명하고, 중요한 세부사항을 포함해주세요:\n\n{text}"
        else:
            prompt_text = f"Please provide a detailed and comprehensive summary of the following text. Include specific details and key points:\n\n{text}"
        
        kwargs = {
            'do_sample': False,
            'truncation': True,  # 토큰 길이 초과시 자동 자르기
            'max_new_tokens': 500,  # 더 긴 요약을 위해 증가
            'min_length': 100     # 더 긴 최소 길이
        }
        
        summary = self.models[language](prompt_text, **kwargs)
        return summary[0]['summary_text']
    
    def _summarize_long_text(self, text, language, recursion_depth=0):
        """긴 텍스트 청크 단위 요약 (재귀 깊이 제한)"""
        # 재귀 깊이 제한 (무한 루프 방지)
        if recursion_depth >= 3:
            st.warning("⚠️ 재귀 깊이 제한에 도달했습니다. 현재 결과를 반환합니다.")
            return text[:1000] + "..." if len(text) > 1000 else text
        
        # 텍스트를 안전한 크기로 분할 (토큰 길이 고려)
        chunks = self._split_text_safely(text, max_chars=800)  # 800자로 증가하여 더 많은 컨텍스트 유지
        
        st.info(f"총 {len(chunks)}개 청크로 분할됨")
        
        # 각 청크를 개별적으로 요약 (한줄 진행률 표시)
        chunk_summaries = []
        progress_text = st.empty()  # 한줄로 업데이트되는 진행률 표시
        
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            # 한줄로 진행률 업데이트
            progress_text.info(f"🔄 청크 요약 진행 중: {i+1}/{len(chunks)}")
            
            try:
                # 프롬프트 기반 청크 요약
                if language == 'ko':
                    prompt_chunk = f"다음 텍스트의 핵심 내용을 상세히 요약해주세요. 구체적인 정보와 세부사항을 포함해주세요:\n\n{chunk}"
                else:
                    prompt_chunk = f"Summarize the key points of the following text in detail, including specific information:\n\n{chunk}"
                
                # 안전한 길이로 요약 (토큰 길이 고려)
                summary = self.models[language](
                    prompt_chunk, 
                    do_sample=False, 
                    truncation=True,  # 토큰 길이 초과시 자동 자르기
                    max_new_tokens=300,  # 더 긴 청크 요약을 위해 증가
                    min_length=80     # 더 긴 최소 길이로 상세한 요약
                )
                chunk_summaries.append(summary[0]['summary_text'])
            except Exception as e:
                st.warning(f"청크 {i+1} 요약 실패: {str(e)}")
                # 실패시 원본 청크의 일부를 요약으로 사용
                fallback_summary = chunk[:150] + "..." if len(chunk) > 150 else chunk
                chunk_summaries.append(fallback_summary)
        
        # 진행률 표시 완료
        progress_text.success(f"✅ 청크 요약 완료: {len(chunk_summaries)}개 청크 처리됨")
        
        # 청크 요약들을 결합
        combined_summaries = ' '.join(chunk_summaries)
        
        # 결합된 텍스트가 여전히 길면 재귀적으로 처리 (더 엄격한 조건)
        if len(combined_summaries) > 2000:  # 1000에서 2000으로 증가
            st.info("🔄 결합된 텍스트가 길어 재귀 요약 진행...")
            return self._summarize_long_text(combined_summaries, language, recursion_depth + 1)
        else:
            # 최종 요약 생성 (안전한 길이로)
            st.info("🔄 최종 요약 생성 중...")
            try:
                # 최종 요약을 위한 프롬프트
                if language == 'ko':
                    final_prompt = f"다음 내용들을 종합하여 체계적이고 상세한 최종 요약을 작성해주세요. 주요 내용을 구체적으로 설명하고, 중요한 세부사항을 모두 포함해주세요:\n\n{combined_summaries}"
                else:
                    final_prompt = f"Please create a comprehensive and detailed final summary by synthesizing the following content. Include all key points and specific details:\n\n{combined_summaries}"
                
                final_summary = self.models[language](
                    final_prompt, 
                    do_sample=False, 
                    truncation=True,  # 토큰 길이 초과시 자동 자르기
                    max_new_tokens=800,  # 더 큰 값으로 설정하여 상세한 요약
                    min_length=300    # 더 큰 최소 길이로 상세한 요약 보장
                )
                return final_summary[0]['summary_text']
            except Exception as e:
                st.warning(f"최종 요약 실패, 청크 요약 결합: {str(e)}")
                return combined_summaries
    
    def _split_text_safely(self, text, max_chars=800):
        """텍스트를 안전한 크기로 분할 (토큰 길이 고려)"""
        # 문장 단위로 분할
        sentences = text.split('. ')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # 현재 청크에 문장을 추가했을 때 길이 확인
            if current_length + sentence_length > max_chars and current_chunk:
                # 현재 청크를 완료하고 새 청크 시작
                chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 2  # '. ' 길이 추가
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append('. '.join(current_chunk))
        
        return chunks
    
    def _postprocess_summary(self, summary, language):
        """요약 후처리 - 구조화된 형태로 개선"""
        if not summary or len(summary.strip()) < 50:
            return summary
        
        # 문장 단위로 분할
        sentences = summary.split('. ')
        if len(sentences) < 3:
            return summary
        
        # 구조화된 요약 생성
        if language == 'ko':
            structured_summary = "## 주요 내용\n\n"
        else:
            structured_summary = "## Key Points\n\n"
        
        # 핵심 문장들을 선별하여 구조화
        key_sentences = []
        for i, sentence in enumerate(sentences):
            if sentence.strip() and len(sentence.strip()) > 20:
                # 문장 앞에 번호나 불릿 포인트 추가
                if language == 'ko':
                    key_sentences.append(f"• {sentence.strip()}")
                else:
                    key_sentences.append(f"• {sentence.strip()}")
        
        # 최대 8-10개의 핵심 문장만 선택
        selected_sentences = key_sentences[:min(10, len(key_sentences))]
        structured_summary += "\n".join(selected_sentences)
        
        # 마지막에 전체 요약 추가
        if language == 'ko':
            structured_summary += "\n\n## 전체 요약\n\n" + summary
        else:
            structured_summary += "\n\n## Overall Summary\n\n" + summary
        
        return structured_summary
    
    def preprocess_text(self, text):
        """텍스트 전처리"""
        # 특수 문자 제거
        text = re.sub(r'[^\w\s가-힣.,!?]', ' ', text)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 연속된 같은 문자 제거 (예: aaaaa -> a)
        text = re.sub(r'(.)\1{3,}', r'\1', text)
        return text.strip()
    
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
