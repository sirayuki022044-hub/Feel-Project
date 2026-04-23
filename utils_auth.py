import streamlit as st
from supabase import create_client, Client

# Supabase 클라이언트 초기화
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# 로그인 상태 체크 함수 (모든 페이지 상단에서 사용)
def check_auth():
    if "user" not in st.session_state:
        st.warning("로그인이 필요한 서비스입니다.")
        st.switch_page("pages/login.py")
        st.stop()

# 로그아웃 함수
def sign_out():
    supabase = get_supabase()
    supabase.auth.sign_out()
    del st.session_state["user"]
    st.switch_page("pages/login.py")