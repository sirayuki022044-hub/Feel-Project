import streamlit as st

# 사이드바를 숨기고 진입점 역할만 수행
st.set_page_config(page_title="FEEL Project", initial_sidebar_state="collapsed")

# CSS를 사용하여 사이드바를 완전히 제거 (선택 사항)
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} [data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/home.py")