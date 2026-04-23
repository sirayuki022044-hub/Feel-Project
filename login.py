import streamlit as st
from utils_auth import get_supabase

st.set_page_config(page_title="로그인", initial_sidebar_state="collapsed")
st.title("🔑 FEEL 프로젝트 로그인")

with st.form("login_form"):
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    submit = st.form_submit_button("로그인")

    if submit:
        try:
            supabase = get_supabase()
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = res.user
            st.success(f"{res.user.user_metadata['full_name']}님, 환영합니다!")
            st.switch_page("pages/home.py")
        except Exception as e:
            st.error("이메일 또는 비밀번호가 올바르지 않습니다.")

if st.button("처음이신가요? 회원가입하기"):
    st.switch_page("pages/join_membership.py")