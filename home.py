import streamlit as st
from utils_auth import check_auth

# 1. 페이지 설정 (로그인 후에는 사이드바를 보여주고 싶다면 "expanded"로 설정)
st.set_page_config(page_title="마음날씨", initial_sidebar_state="expanded")

# 2. 로그인 여부 즉시 확인 (인증 안 된 사용자는 login.py로 튕겨냄)
check_auth()

# --- 이후에 기존 프로그램 로직 작성 ---
st.title("🏠 홈 화면")
st.write(f"{st.session_state.user.user_metadata['full_name']}님, 오늘 하루는 어떠신가요?")