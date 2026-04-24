import streamlit as st
from utils_auth import get_supabase

st.set_page_config(page_title="회원가입", initial_sidebar_state="collapsed")
st.title("🌱 FEEL 프로젝트 회원가입")

with st.form("signup_form"):
    email = st.text_input("이메일")
    full_name = st.text_input("성명")
    password = st.text_input("비밀번호", type="password")
    submit = st.form_submit_button("가입하기")

    if submit:
        supabase = get_supabase()
        # metadata에 성명을 함께 저장
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })

        if res.user:
            st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
            st.switch_page("pages/login.py")
        else:
            st.error("가입 실패: 정보를 확인해주세요.")

if st.button("로그인 화면으로 돌아가기"):
    st.switch_page("pages/login.py")
