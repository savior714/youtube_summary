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

# ffmpeg 설치 안내
st.info("""
💡 **첫 사용자 안내**: 
- 자막이 없는 영상의 경우 음성 인식이 필요합니다
- Windows 사용자는 [ffmpeg 다운로드](https://www.gyan.dev/ffmpeg/builds/) 후 PATH에 추가하세요
- 설치 후 브라우저를 새로고침하세요
""")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 요약 옵션
    summary_length = st.selectbox(
        "요약 길이",
        ["짧게 (50-100자)", "보통 (100-150자)", "길게 (150-200자)"],
        index=1
    )
    
    # 요약 결과 언어 설정
    summary_language = st.selectbox(
        "요약 결과 언어",
        ["한국어", "영어"],
        index=0,  # 기본값: 한국어
        help="요약 결과를 어떤 언어로 생성할지 선택하세요"
    )
    
    # 고급 옵션
    with st.expander("고급 설정"):
        show_transcript = st.checkbox("원본 자막 보기", value=False)
        use_whisper = st.checkbox("자막 없으면 음성 인식 사용", value=True, help="자막이 없는 영상의 경우 Whisper로 음성 인식")
        
    # 모델 정보
    with st.expander("모델 정보"):
        st.success("✅ BART 요약 모델 사용")
        st.info("🎤 Whisper 음성 인식 모델 사용 가능")
        
    # ffmpeg 상태 확인
    with st.expander("시스템 상태"):
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
            
            # 4단계: 요약 언어 설정
            if summary_language == "한국어":
                target_lang = "ko"
            else:
                target_lang = "en"
            
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
                language=target_lang,
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