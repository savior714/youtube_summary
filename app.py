import streamlit as st
from youtube_utils import extract_video_id, get_transcript, format_transcript, detect_language
from summarizer import Summarizer
import time

# ?섏씠吏 ?ㅼ젙
st.set_page_config(
    page_title="?좏뒠釉??붿빟 ?쒕퉬??,
    page_icon="?벟",
    layout="wide"
)

# ?쒕ぉ
st.title("?벟 ?섎쭔???좏뒠釉??붿빟 ?쒕퉬??)
st.markdown("---")

# ?ъ씠?쒕컮 ?ㅼ젙
with st.sidebar:
    st.header("?숋툘 ?ㅼ젙")
    
    # ?붿빟 ?듭뀡
    summary_length = st.selectbox(
        "?붿빟 湲몄씠",
        ["吏㏐쾶 (50-100??", "蹂댄넻 (100-150??", "湲멸쾶 (150-200??"],
        index=1
    )
    
    # ?몄뼱 ?ㅼ젙
    language = st.selectbox(
        "?몄뼱 ?ㅼ젙",
        ["?먮룞 媛먯?", "?쒓뎅??, "?곸뼱"],
        index=0
    )
    
    # 怨좉툒 ?듭뀡
    with st.expander("怨좉툒 ?ㅼ젙"):
        show_transcript = st.checkbox("?먮낯 ?먮쭑 蹂닿린", value=False)
        chunk_size = st.slider("泥?겕 ?ш린", 500, 2000, 1000)

# 硫붿씤 而⑦뀗痢?col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("?뵕 ?좏뒠釉?URL ?낅젰")
    url = st.text_input(
        "?좏뒠釉?留곹겕瑜??낅젰?섏꽭??",
        placeholder="https://www.youtube.com/watch?v=...",
        help="?좏뒠釉??곸긽 URL???낅젰?섎㈃ ?먮룞?쇰줈 ?먮쭑??異붿텧?섍퀬 ?붿빟?⑸땲??"
    )

with col2:
    st.subheader("?뱤 ?ъ슜踰?)
    st.markdown("""
    1. ?좏뒠釉?URL ?낅젰
    2. ?ㅼ젙 議곗젙 (?좏깮?ы빆)
    3. '?붿빟?섍린' 踰꾪듉 ?대┃
    4. 寃곌낵 ?뺤씤 諛??ㅼ슫濡쒕뱶
    """)

# ?붿빟 ?ㅽ뻾
if st.button("?? ?붿빟?섍린", type="primary"):
    if not url:
        st.warning("?좏뒠釉?URL???낅젰?댁＜?몄슂.")
    else:
        # 吏꾪뻾 ?곹솴 ?쒖떆
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1?④퀎: 鍮꾨뵒??ID 異붿텧
            status_text.text("鍮꾨뵒??ID 異붿텧 以?..")
            progress_bar.progress(20)
            
            video_id = extract_video_id(url)
            if not video_id:
                st.error("?좏슚?섏? ?딆? ?좏뒠釉?URL?낅땲??")
                st.stop()
            
            # 2?④퀎: ?먮쭑 異붿텧
            status_text.text("?먮쭑 異붿텧 以?..")
            progress_bar.progress(40)
            
            transcript_data = get_transcript(video_id)
            if not transcript_data:
                st.error("?먮쭑??李얠쓣 ???놁뒿?덈떎. ?먮쭑???덈뒗 ?곸긽???좏깮?댁＜?몄슂.")
                st.stop()
            
            # 3?④퀎: ?띿뒪??蹂??            status_text.text("?띿뒪??蹂??以?..")
            progress_bar.progress(60)
            
            transcript_text = format_transcript(transcript_data)
            
            # 4?④퀎: ?몄뼱 媛먯?
            detected_lang = detect_language(transcript_text)
            if language == "?먮룞 媛먯?":
                final_lang = detected_lang
            elif language == "?쒓뎅??:
                final_lang = "ko"
            else:
                final_lang = "en"
            
            # 5?④퀎: ?붿빟 ?앹꽦
            status_text.text("AI ?붿빟 ?앹꽦 以?..")
            progress_bar.progress(80)
            
            # ?붿빟 湲몄씠 ?ㅼ젙
            length_map = {
                "吏㏐쾶 (50-100??": (50, 100),
                "蹂댄넻 (100-150??": (100, 150), 
                "湲멸쾶 (150-200??": (150, 200)
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
            status_text.text("?꾨즺!")
            
            # 寃곌낵 ?쒖떆
            st.success("???붿빟???꾨즺?섏뿀?듬땲??")
            
            # ?붿빟 寃곌낵
            st.subheader("?뱷 ?붿빟 寃곌낵")
            st.write(summary)
            
            # ?ㅼ슫濡쒕뱶 踰꾪듉
            st.download_button(
                label="?뱿 ?붿빟 寃곌낵 ?ㅼ슫濡쒕뱶",
                data=summary,
                file_name=f"youtube_summary_{video_id}.txt",
                mime="text/plain"
            )
            
            # ?먮낯 ?먮쭑 ?쒖떆 (?듭뀡)
            if show_transcript:
                with st.expander("?뱞 ?먮낯 ?먮쭑 蹂닿린"):
                    st.text_area("?먮쭑 ?댁슜:", transcript_text, height=300)
            
            # ?듦퀎 ?뺣낫
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("?먮낯 湲몄씠", f"{len(transcript_text):,}??)
            with col2:
                st.metric("?붿빟 湲몄씠", f"{len(summary):,}??)
            with col3:
                compression_ratio = (1 - len(summary) / len(transcript_text)) * 100
                st.metric("?뺤텞瑜?, f"{compression_ratio:.1f}%")
                
        except Exception as e:
            st.error(f"?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎: {str(e)}")
            st.info("?ㅻⅨ ?곸긽?쇰줈 ?쒕룄?대낫?몄슂.")

# ?명꽣
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>?뮕 <strong>??</strong> ?먮쭑???덈뒗 ?곸긽?먯꽌留??묐룞?⑸땲?? ?먮룞 ?앹꽦 ?먮쭑??吏?먰빀?덈떎.</p>
    <p>?뵩 <strong>臾몄젣 ?닿껐:</strong> ?쇰? ?곸긽? ?먮쭑???녾굅??鍮꾧났媛쒖씪 ???덉뒿?덈떎.</p>
</div>
""", unsafe_allow_html=True)
