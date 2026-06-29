import streamlit as st
import datetime
from supabase import create_client, Client

# ----------------------------------------------------------------
# ⚙️ Supabase 환경 설정
# ----------------------------------------------------------------
SUPABASE_URL = "https://badsgkosnlrxbaubuowd.supabase.co"
SUPABASE_KEY = "sb_publishable_fHuK1bwD1LdwopIAcL9B_Q_D8tFYAtJ"

# 🔒 관리자 삭제용 비밀번호 (선생님 원하시는 비밀번호로 변경 가능)
ADMIN_PASSWORD = "1234"


@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL.strip(), SUPABASE_KEY.strip())


try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Supabase 초기화 실패: {e}")

# ----------------------------------------------------------------
# 🧭 상단 탭 메뉴 구성 (요청하신 대로 방명록 탭만 노출)
# ----------------------------------------------------------------
# 나중에 다른 메뉴를 합치고 싶으시면 ["🎨 동아리 방명록", "☀️ 마인드 웨더"] 형태로 늘리시면 됩니다.
tab_guestbook, = st.tabs(["🎨 동아리 방명록"])

with tab_guestbook:
    st.title("🎨 문화예술동아리 방명록")
    st.markdown("### 우리 동아리 활동은 어땠나요? 자유롭게 소감을 남겨주세요! ✨")
    st.write("로그인 없이 누구나 따뜻한 한 마디를 남길 수 있는 공간입니다.")
    st.markdown("---")

    # 1. 방명록 작성 구역
    with st.form("guestbook_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            visitor_name = st.text_input("작성자/닉네임", placeholder="예: 홍길동", max_chars=10)
        with col2:
            comment = st.text_input("남길 말씀", placeholder="오늘 활동 소감이나 응원의 메시지를 적어주세요!")

        submit_btn = st.form_submit_button("💌 소감 등록하기", use_container_width=True)

        if submit_btn:
            if not visitor_name or not comment:
                st.error("닉네임과 남길 말씀을 모두 입력해주세요.")
            else:
                with st.spinner("방명록을 안전하게 배달 중입니다..."):
                    try:
                        guest_data = {
                            "visitor_name": visitor_name,
                            "comment": comment
                        }
                        supabase.table("guestbook").insert(guest_data).execute()
                        st.success("🎉 방명록이 성공적으로 등록되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"방명록 저장 실패: {e}")

    st.markdown("---")

    # 2. 실시간 방명록 목록 출력 및 삭제 구역
    st.subheader("📋 학생들이 남긴 소감 한 줄")

    try:
        guest_response = supabase.table("guestbook").select("*").order("created_at", desc=True).execute()
        guests = guest_response.data

        if not guests:
            st.info("아직 작성된 방명록이 없습니다. 첫 번째 응원의 한 마디를 남겨보세요!")
        else:
            for guest in guests:
                date_time = guest['created_at'].replace("T", " ")[:16] if guest['created_at'] else ""

                with st.container(border=True):
                    # 글 내용 레이아웃 분할 (내용 열과 삭제 버튼 열)
                    text_col, btn_col = st.columns([5, 1])

                    with text_col:
                        st.markdown(f"#### 💬 {guest['comment']}")
                        st.caption(f"✍️ **작성자**: {guest['visitor_name']}  |  🕒 {date_time}")

                    with btn_col:
                        # 각 글마다 고유한 삭제 버튼 생성
                        delete_requested = st.button("🗑️ 삭제", key=f"del_{guest['id']}", use_container_width=True)

                        if delete_requested:
                            # 세션 상태를 이용해 어떤 글을 지울지 임시 저장
                            st.session_state[f"confirm_delete_{guest['id']}"] = True

                    # 삭제 버튼을 눌렀을 때만 비밀번호 입력창 등장
                    if st.session_state.get(f"confirm_delete_{guest['id']}", False):
                        password_input = st.text_input(
                            f"'{guest['visitor_name']}'님의 글을 삭제하려면 비밀번호를 입력하세요",
                            type="password",
                            key=f"pass_{guest['id']}"
                        )

                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("확인", key=f"conf_btn_{guest['id']}", use_container_width=True):
                                if password_input == ADMIN_PASSWORD:
                                    try:
                                        # Supabase에서 해당 ID의 데이터 삭제
                                        supabase.table("guestbook").delete().eq("id", guest['id']).execute()
                                        st.success("글이 성공적으로 삭제되었습니다.")
                                        st.session_state[f"confirm_delete_{guest['id']}"] = False
                                        st.rerun()
                                    except Exception as delete_error:
                                        st.error(f"삭제 중 오류가 발생했습니다: {delete_error}")
                                else:
                                    st.error("비밀번호가 일치하지 않습니다.")
                        with col_cancel:
                            if st.button("취소", key=f"cancel_btn_{guest['id']}", use_container_width=True):
                                st.session_state[f"confirm_delete_{guest['id']}"] = False
                                st.rerun()

    except Exception as e:
        st.error(f"방명록을 불러오는 중 오류가 발생했습니다: {e}")