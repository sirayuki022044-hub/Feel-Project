import streamlit as st
from utils_auth import check_auth

# 1. 페이지 설정 (로그인 후에는 사이드바를 보여주고 싶다면 "expanded"로 설정)
st.set_page_config(page_title="마음날씨", initial_sidebar_state="expanded")

# 2. 로그인 여부 즉시 확인 (인증 안 된 사용자는 login.py로 튕겨냄)
check_auth()

# --- 이후에 기존 프로그램 로직 작성 ---
st.title("🏠 홈 화면")
st.write(f"{st.session_state.user.user_metadata['full_name']}님, 오늘 하루는 어떠신가요?")
import streamlit as st
from utils_auth import check_auth, get_supabase
from datetime import datetime

# 1. 인증 및 페이지 설정
st.set_page_config(page_title="Emotional Diary", layout="centered")
check_auth()

# 2. 감정별 설정 (색상, 점수, 아이콘)
emotion_config = {
    "기쁨": {"color": "#FFF9C4", "score": 100, "icon": "☀️"},    # 노란색
    "괜찮음": {"color": "#C8E6C9", "score": 80, "icon": "🌤️"},   # 초록색
    "그저그럼": {"color": "#F5F5F5", "score": 60, "icon": "☁️"},  # 회색
    "슬픔": {"color": "#BBDEFB", "score": 40, "icon": "🌧️"},   # 파란색
    "화가남": {"color": "#FFCDD2", "score": 20, "icon": "⚡"}    # 빨간색
}

# 3. 감정 선택 및 배경색 변경 로직
st.title("📖 오늘의 마음 일기")
selected_emotion = st.selectbox("오늘의 감정을 선택하세요", list(emotion_config.keys()))

# 배경색 변경을 위한 CSS 주입
bg_color = emotion_config[selected_emotion]["color"]
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        transition: background-color 0.5s ease;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. 일기 입력 폼
with st.form("diary_form"):
    date = st.date_input("날짜 선택", datetime.now())
    content = st.text_area("오늘의 이야기를 3~4줄 내외로 적어보세요.", placeholder="여기에 작성하세요...")
    submit = st.form_submit_button("저장하기")

    if submit:
        if len(content.strip()) < 10:
            st.warning("일기를 조금 더 정성껏 써볼까요?")
        else:
            supabase = get_supabase()
            data = {
                "user_id": st.session_state.user.id,
                "date": str(date),
                "emotion": selected_emotion,
                "score": emotion_config[selected_emotion]["score"],
                "content": content,
                "icon": emotion_config[selected_emotion]["icon"]
            }
            # Supabase 'diaries' 테이블에 저장
            res = supabase.table("diaries").insert(data).execute()
            st.success("오늘의 마음 날씨가 성공적으로 기록되었습니다!")