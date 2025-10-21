import streamlit as st
from youtube_utils import extract_video_id, get_transcript, format_transcript, detect_language
from summarizer import Summarizer
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

# OpenAI API 키 설정 안내
if not os.getenv('OPENAI_API_KEY'):
    st.info("💡 **OpenAI API 키를 설정하면 GPT 모델로 더 정확한 요약을 받을 수 있습니다.** 환경변수 `OPENAI_API_KEY`를 설정하세요.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 요약 옵션
    summary_length = st.selectbox(
        "요약 길이",
        ["짧게 (50-100자)", "보통 (100-150자)", "길게 (150-200자)"],
        index=1
    )
    
    # 언어 설정
    language = st.selectbox(
        "언어 설정",
        ["자동 감지", "한국어", "영어"],
        index=0
    )
    
    # 고급 옵션
    with st.expander("고급 설정"):
        show_transcript = st.checkbox("원본 자막 보기", value=False)
        use_whisper = st.checkbox("자막 없으면 음성 인식 사용", value=True, help="자막이 없는 영상의 경우 Whisper로 음성 인식")
        
    # 모델 정보
    with st.expander("모델 정보"):
        if os.getenv('OPENAI_API_KEY'):
            st.success("✅ OpenAI GPT 모델 사용 가능")
        else:
            st.warning("⚠️ BART 모델 사용 (OpenAI API 키 없음)")
        
        st.info("🎤 Whisper 음성 인식 모델 사용 가능")

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
            
            transcript_data = get_transcript(url)
            if not transcript_data:
                st.error("자막/음성 추출에 실패했습니다.")
                st.stop()
            
            # 3단계: 텍스트 변환
            status_text.text("텍스트 변환 중...")
            progress_bar.progress(50)
            
            transcript_text = format_transcript(transcript_data)
            
            # 4단계: 언어 감지
            detected_lang = detect_language(transcript_text)
            if language == "자동 감지":
                final_lang = detected_lang
            elif language == "한국어":
                final_lang = "ko"
            else:
                final_lang = "en"
            
            # 5단계: 요약 생성
            status_text.text("AI 요약 생성 중...")
            progress_bar.progress(70)
            
            # 요약 길이 설정
            length_map = {
                "짧게 (50-100자)": (50, 100),
                "보통 (100-150자)": (100, 150), 
                "길게 (150-200자)": (150, 200)
            }
            min_len, max_len = length_map[summary_length]
            
            summarizer = Summarizer()
            summary = summarizer.summarize_text(
                transcript_text, 
                language=final_lang,
                max_length=max_len,
                min_length=min_len
            )
            
            progress_bar.progress(100)
            status_text.text("완료!")
            
            # 결과 표시
            st.success("✅ 요약이 완료되었습니다!")
            
            # 요약 결과
            st.subheader("📝 요약 결과")
            st.write(summary)
            
            # 다운로드 버튼
            st.download_button(
                label="📥 요약 결과 다운로드",
                data=summary,
                file_name=f"youtube_summary_{video_id}.txt",
                mime="text/plain"
            )
            
            # 원본 자막 표시 (옵션)
            if show_transcript:
                with st.expander("📄 원본 자막 보기"):
                    st.text_area("자막 내용:", transcript_text, height=300)
            
            # 통계 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("원본 길이", f"{len(transcript_text):,}자")
            with col2:
                st.metric("요약 길이", f"{len(summary):,}자")
            with col3:
                compression_ratio = (1 - len(summary) / len(transcript_text)) * 100
                st.metric("압축률", f"{compression_ratio:.1f}%")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("다른 영상으로 시도해보세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>팁:</strong> 자막이 있는 영상에서만 작동합니다. 자동 생성 자막도 지원합니다.</p>
    <p>🎤 <strong>음성 인식:</strong> 자막이 없는 영상은 Whisper로 음성 인식합니다.</p>
    <p>🤖 <strong>AI 요약:</strong> OpenAI API 키를 설정하면 GPT 모델을 사용합니다.</p>
    <p>🔧 <strong>문제 해결:</strong> 일부 영상은 자막이 없거나 비공개일 수 있습니다.</p>
</div>
""", unsafe_allow_html=True)