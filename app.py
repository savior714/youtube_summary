import streamlit as st
from youtube_utils import extract_video_id, get_transcript, format_transcript, detect_language
from summarizer import Summarizer
from api_summarizer import APISummarizer
from hybrid_summarizer import HybridSummarizer
from gpu_utils import display_gpu_status, GPUDetector
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="유튜브 요약 서비스",
    page_icon="📺",
    layout="wide"
)

# 제목
st.title("📺 나만의 유튜브 요약 서비스")
st.markdown("---")


# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 자동 모델 선택 안내
    with st.expander("🤖 LongT5 적응형 모델", expanded=False):
        st.info("🎯 VRAM에 따라 자동 최적화")
        st.caption("12GB+: Full Precision | 8GB+: 8bit | 4GB+: 8bit | 2GB+: 4bit | CPU: BART")
    
    # 요약 결과 언어 설정
    summary_language = st.selectbox(
        "요약 결과 언어",
        ["한국어", "영어"],
        index=0,  # 기본값: 한국어
        help="요약 결과를 어떤 언어로 생성할지 선택하세요"
    )
    
    # 고급 옵션
    with st.expander("고급 설정", expanded=True):
        show_transcript = st.checkbox("원본 자막 보기", value=False)
        
        
    # GPU 상태 확인
    with st.expander("🖥️ GPU 상태", expanded=True):
        display_gpu_status()
    
    # ffmpeg 상태 확인
    with st.expander("🔧 시스템 상태", expanded=True):
        ffmpeg_found = False
        ffmpeg_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",  # 권장 설치 경로
            "C:\\ffmpegWbin\\ffmpeg.exe", 
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "ffmpeg"  # PATH에 있는 경우
        ]
        
        for path in ffmpeg_paths:
            try:
                import subprocess
                if path == "ffmpeg":
                    result = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=5)
                else:
                    result = subprocess.run([path, "-version"], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    st.success(f"✅ ffmpeg 발견: {path}")
                    ffmpeg_found = True
                    break
            except:
                continue
        
        if not ffmpeg_found:
            st.warning("⚠️ ffmpeg 미설치 또는 PATH 미설정")
            st.info("""
            💡 **권장 설치 방법:**
            1. [ffmpeg 다운로드](https://www.gyan.dev/ffmpeg/builds/)
            2. `C:\\ffmpeg\\` 폴더에 압축 해제
            3. 최종 경로: `C:\\ffmpeg\\bin\\ffmpeg.exe`
            """)

# 저장된 결과가 있으면 표시
if 'summary_result' in st.session_state:
    result = st.session_state['summary_result']
    
    # 결과 표시
    st.success("✅ 요약이 완료되었습니다!")
    
    # 요약 방식 표시
    st.info(f"📊 사용된 요약 방식: {result['summary_method']}")
    
    # 요약 결과
    st.subheader("📝 요약 결과")
    st.write(result['summary'])
    
    # 다운로드 버튼 (초기화 방지)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            label="📥 요약 결과 다운로드",
            data=result['summary'],
            file_name=f"youtube_summary_{result['video_id']}.txt",
            mime="text/plain",
            key="download_summary",
            use_container_width=True
        )
    with col2:
        if st.button("🔄 새로 요약하기", use_container_width=True):
            # session_state 초기화
            del st.session_state['summary_result']
            st.rerun()
    
    # 원본 자막 표시 (옵션)
    if result['show_transcript']:
        with st.expander("📄 원본 자막 보기"):
            st.text_area("자막 내용:", result['transcript_text'], height=300)
    
    # 통계 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("원본 길이", f"{len(result['transcript_text']):,}자")
    with col2:
        st.metric("요약 길이", f"{len(result['summary']):,}자")
    with col3:
        compression_ratio = (1 - len(result['summary']) / len(result['transcript_text'])) * 100
        st.metric("압축률", f"{compression_ratio:.1f}%")
    
    st.markdown("---")

# 메인 컨텐츠
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔗 유튜브 URL 입력")
    url = st.text_input(
        "유튜브 링크를 입력하세요:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="유튜브 영상 URL을 입력하면 자동으로 자막을 추출하고 요약합니다."
    )

with col2:
    st.subheader("📊 사용법")
    st.markdown("""
    1. 유튜브 URL 입력
    2. 설정 조정 (선택사항)
    3. '요약하기' 버튼 클릭
    4. 결과 확인 및 다운로드
    """)

# 요약 실행
if st.button("🚀 요약하기", type="primary"):
    if not url:
        st.warning("유튜브 URL을 입력해주세요.")
    else:
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1단계: 비디오 ID 추출
            status_text.text("비디오 ID 추출 중...")
            progress_bar.progress(10)
            
            video_id = extract_video_id(url)
            if not video_id:
                st.error("유효하지 않은 유튜브 URL입니다.")
                st.stop()
            
            # 2단계: 자막/음성 추출
            status_text.text("자막/음성 추출 중...")
            progress_bar.progress(30)
            
            transcript_data = get_transcript(url, use_whisper=True)
            if not transcript_data:
                st.error("자막/음성 추출에 실패했습니다.")
                st.stop()
            
            # 3단계: 텍스트 변환
            status_text.text("텍스트 변환 중...")
            progress_bar.progress(50)
            
            transcript_text = format_transcript(transcript_data)
            
            # 4단계: 원본 언어 감지 및 요약 언어 설정
            detected_lang = detect_language(transcript_text)
            st.info(f"원본 텍스트 언어 감지: {'한국어' if detected_lang == 'ko' else '영어'}")
            
            # 원본 언어에 맞는 모델 사용 (품질 우선)
            if detected_lang == 'ko':
                # 한국어 원본 → 한국어 요약 (최적)
                target_lang = "ko"
                st.info("✅ 한국어 원본 → 한국어 요약 (최적 품질)")
            else:
                # 영어 원본 → 영어 요약 (최적)
                target_lang = "en"
                st.info("✅ 영어 원본 → 영어 요약 (최적 품질)")
            
            # 사용자가 다른 언어를 원하는 경우 강제로 원본 언어 사용
            if (detected_lang == 'ko' and summary_language == "영어") or \
               (detected_lang == 'en' and summary_language == "한국어"):
                st.warning("⚠️ 원본 언어와 다른 언어로 요약하면 품질이 심각하게 떨어집니다.")
                st.info("💡 자동으로 원본 언어에 맞는 모델을 사용합니다.")
                if detected_lang == 'ko':
                    target_lang = "ko"
                    st.info("🔄 한국어 모델로 변경됨")
                else:
                    target_lang = "en"
                    st.info("🔄 영어 모델로 변경됨")
            
            # 5단계: 요약 생성
            status_text.text("AI 요약 생성 중...")
            progress_bar.progress(70)
            
            # Whisper 처리 시간 안내
            if "음성 인식" in st.session_state.get('last_method', ''):
                st.info("""
                ⏱️ **처리 시간 안내**
                - 현재 Whisper 음성 인식이 진행 중입니다
                - 파일 크기에 따라 5-15분 소요될 수 있습니다
                - 브라우저를 닫지 마세요 (처리가 중단됩니다)
                """)
            
            # 길이 제한 제거 - 자동으로 최적 길이 결정
            st.info("📏 요약 길이: 자동 조절 (제한 없음)")
            
            # 자동 모델 선택으로 요약
            summarizer = Summarizer()
            summary = summarizer.summarize_text(
                transcript_text, 
                language=target_lang
            )
            
            # 사용된 모델 정보 표시
            detector = GPUDetector()
            device_info = detector.get_device_info()
            vram_gb = device_info["vram_gb"]
            device = device_info["device"]
            gpu_name = device_info["gpu_name"]
            
            if device == "cuda":
                if vram_gb >= 12:
                    summary_method = f"LongT5 Full Precision (GPU: {gpu_name})"
                elif vram_gb >= 8:
                    summary_method = f"LongT5 8bit (GPU: {gpu_name})"
                elif vram_gb >= 4:
                    summary_method = f"LongT5 8bit (GPU: {gpu_name})"
                elif vram_gb >= 2:
                    summary_method = f"LongT5 4bit (GPU: {gpu_name})"
                else:
                    summary_method = f"LongT5 4bit (GPU: {gpu_name})"
            else:
                summary_method = "BART (CPU)"
            
            progress_bar.progress(100)
            status_text.text("완료!")
            
            # 결과를 session_state에 저장
            st.session_state['summary_result'] = {
                'summary': summary,
                'summary_method': summary_method,
                'video_id': video_id,
                'transcript_text': transcript_text,
                'show_transcript': show_transcript
            }
            
            # 결과가 저장되었으므로 페이지 새로고침
            st.rerun()
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.exception(e)  # 상세한 오류 정보 표시
            st.info("다른 영상으로 시도해보세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>팁:</strong> 자막이 있는 영상에서만 작동합니다. 자동 생성 자막도 지원합니다.</p>
    <p>🎤 <strong>음성 인식:</strong> 자막이 없는 영상은 Whisper로 음성 인식합니다.</p>
    <p>🔧 <strong>문제 해결:</strong> ffmpeg가 설치되어 있지 않으면 음성 인식이 실패할 수 있습니다.</p>
</div>
""", unsafe_allow_html=True)