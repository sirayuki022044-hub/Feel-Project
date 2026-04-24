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
import pandas as pd
import plotly.express as px
from utils_auth import check_auth, get_supabase

# 1. 인증 및 페이지 설정
st.set_page_config(page_title="Mind Weather", layout="wide")
check_auth()

st.title("📊 나의 마음날씨 그래프")

# 2. 데이터 불러오기 및 가공
supabase = get_supabase()
res = supabase.table("diaries").select("date, score, emotion, icon").eq("user_id", st.session_state.user.id).execute()

if res.data:
    # Pandas 데이터프레임 생성
    df = pd.DataFrame(res.data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date') # 날짜순 정렬

    # 3. 그래프 시각화 (Plotly)
    fig = px.line(
        df, x='date', y='score',
        markers=True,
        text='icon', # 그래프 위에 날씨 아이콘 표시
        title="시간에 따른 마음 온도 변화"
    )

    # 4. 그래프 디자인 커스텀
    fig.update_traces(textposition="top center", line_color="#FF4B4B", line_width=3)
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="마음 점수",
        yaxis=dict(
            tickvals=[20, 40, 60, 80, 100],
            ticktext=["⚡ 화남(20)", "🌧️ 슬픔(40)", "☁️ 그저그럼(60)", "🌤️ 괜찮음(80)", "☀️ 기쁨(100)"],
            range=[10, 110]
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # 5. 하단 데이터 표 (선택사항)
    with st.expander("상세 기록 보기"):
        st.dataframe(df[['date', 'emotion', 'score']].rename(columns={'date':'날짜', 'emotion':'감정', 'score':'점수'}))
else:
    st.info("아직 기록된 일기가 없습니다. 'Emotional Diary' 페이지에서 첫 일기를 써보세요!")
