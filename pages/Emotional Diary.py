import streamlit as st
from utils_auth import check_auth, get_supabase
from datetime import datetime

# 1. 인증 및 페이지 설정
st.set_page_config(page_title="Emotional Diary", layout="centered")
check_auth()

# 2. 감정별 설정
emotion_config = {
    "기쁨": {"color": "#FFF9C4", "score": 100, "icon": "☀️"},
    "괜찮음": {"color": "#C8E6C9", "score": 80, "icon": "🌤️"},
    "그저그럼": {"color": "#F5F5F5", "score": 60, "icon": "☁️"},
    "슬픔": {"color": "#BBDEFB", "score": 40, "icon": "🌧️"},
    "화가남": {"color": "#FFCDD2", "score": 20, "icon": "⚡"}
}

# 수정할 일기 데이터를 저장할 session_state 초기화
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
    st.session_state.edit_diary_id = None
    st.session_state.edit_date = None
    st.session_state.edit_content = ""
    st.session_state.edit_emotion = "기쁨"

# 3. 감정 선택 및 배경색 변경 로직
st.title("📖 오늘의 마음 일기")

# 수정 모드일 때는 기존 일기의 감정을 기본값으로 설정
default_emotion = st.session_state.edit_emotion if st.session_state.edit_mode else "기쁨"
default_index = list(emotion_config.keys()).index(default_emotion)

selected_emotion = st.radio(
    "오늘의 감정을 선택하세요",
    list(emotion_config.keys()),
    index=default_index,
    format_func=lambda x: f"{emotion_config[x]['icon']} {x}",
    horizontal=True
)

bg_color = emotion_config[selected_emotion]["color"]
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        transition: background-color 0.5s ease;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. 일기 작성 / 수정 폼
form_title = "✏️ 일기 수정하기" if st.session_state.edit_mode else "✍️ 오늘의 이야기 기록"
with st.form("diary_form"):
    st.write(f"### {form_title}")

    # 날짜 및 내용 기본값 설정 (수정 모드 반영)
    default_date = st.session_state.edit_date if st.session_state.edit_mode else datetime.now().date()
    # 수정 모드일 때는 날짜 변경을 막아 1일 1기록 유지
    date = st.date_input("날짜 선택", default_date, disabled=st.session_state.edit_mode)

    content = st.text_area(
        "내용을 적어보세요.",
        value=st.session_state.edit_content,
        placeholder="오늘 하루는 어땠나요? 맞춤법에 맞게 정성껏 적어보세요..."
    )

    submit_label = "수정 완료하기" if st.session_state.edit_mode else "저장하기"
    submit = st.form_submit_button(submit_label)

    # 수정 취소 버튼 (수정 모드일 때만 표시)
    if st.session_state.edit_mode:
        if st.form_submit_button("❌ 수정 취소"):
            st.session_state.edit_mode = False
            st.rerun()

    if submit:
        if len(content.strip()) < 10:
            st.warning("일기를 조금 더 정성껏 써볼까요?")
        else:
            supabase = get_supabase()
            current_user_id = st.session_state.user.id

            data = {
                "user_id": current_user_id,
                "date": str(date),
                "emotion": selected_emotion,
                "score": emotion_config[selected_emotion]["score"],
                "content": content,
                "icon": emotion_config[selected_emotion]["icon"]
            }

            try:
                if st.session_state.edit_mode:
                    # [수정 모드] 선택된 특정 일기 ID를 업데이트
                    supabase.table("diaries").update(data).eq("id", st.session_state.edit_diary_id).execute()
                    st.success("맞춤법 및 내용이 성공적으로 수정되었습니다! ✨")
                    st.session_state.edit_mode = False  # 수정 완료 후 모드 해제
                else:
                    # [일반 저장 모드] 1일 1회 중복 체크
                    existing_diary = supabase.table("diaries").select("id").eq("user_id", current_user_id).eq("date",
                                                                                                              str(date)).execute()

                    if existing_diary.data:
                        diary_id = existing_diary.data[0]["id"]
                        supabase.table("diaries").update(data).eq("id", diary_id).execute()
                        st.success("오늘 이미 작성한 일기가 있어 새로운 내용으로 수정되었습니다! 🔄")
                    else:
                        supabase.table("diaries").insert(data).execute()
                        st.success("오늘의 마음이 성공적으로 기록되었습니다! 🎉")

                st.rerun()

            except Exception as e:
                st.error(f"저장 중 오류가 발생했습니다: {e}")

# 5. 내가 기록한 일기 조회 및 수정 호출 로직
st.write("---")
st.subheader("🔍 나의 지난 마음 기록")

supabase = get_supabase()
current_user_id = st.session_state.user.id

try:
    response = supabase.table("diaries").select("*").eq("user_id", current_user_id).order("date", desc=True).execute()
    diaries = response.data

    if not diaries:
        st.info("아직 기록된 마음 일기가 없습니다.")
    else:
        for diary in diaries:
            with st.expander(f"📅 {diary['date']} | {diary.get('icon', '📝')} {diary['emotion']}"):
                st.write(diary['content'])
                st.caption(f"마음 점수: {diary['score']}점")

                # 💡 핵심 추가: 각 일기 하단에 맞춤법 수정 버튼 배치
                # st.button은 key 값이 고유해야 하므로 diary['id']를 활용합니다.
                if st.button("📝 맞춤법 수정하기", key=f"edit_{diary['id']}"):
                    # 버튼을 누르면 해당 일기 데이터를 session_state에 담고 수정 모드로 전환
                    st.session_state.edit_mode = True
                    st.session_state.edit_diary_id = diary['id']
                    st.session_state.edit_date = datetime.strptime(diary['date'], "%Y-%m-%d").date()
                    st.session_state.edit_content = diary['content']
                    st.session_state.edit_emotion = diary['emotion']
                    st.rerun()  # 상단 폼으로 데이터를 보내기 위해 리런

except Exception as e:
    st.error(f"기록을 불러오는 중 오류가 발생했습니다: {e}")
