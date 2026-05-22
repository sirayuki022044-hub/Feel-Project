import streamlit as st
import pandas as pd
import plotly.express as px
from utils_auth import check_auth, get_supabase

# 1. 인증 및 페이지 설정
st.set_page_config(page_title="Mind Weather", layout="wide")
check_auth()

st.title("📊 나의 마음날씨 그래프")
st.caption("💡 그래프 위의 점을 클릭하면 그날 작성한 일기 팝업이 나타납니다.")


# 팝업(다이얼로그) 창 정의
@st.dialog("📖 그날의 마음 일기")
def show_diary_popup(diary_row):
    formatted_date = diary_row['date'].strftime('%Y년 %m월 %d일')
    st.write(f"### {formatted_date} ({diary_row['icon']} {diary_row['emotion']})")
    st.write(f"**마음 점수:** {diary_row['score']}점")
    st.write("---")
    st.write(diary_row['content'])


# 2. 데이터 불러오기 및 가공 (content 추가)
supabase = get_supabase()
res = supabase.table("diaries").select("date, score, emotion, icon, content").eq("user_id",
                                                                                 st.session_state.user.id).execute()

if res.data:
    # Pandas 데이터프레임 생성
    df = pd.DataFrame(res.data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')  # 날짜순 정렬

    # 3. 그래프 시각화 (Plotly)
    fig = px.line(
        df, x='date', y='score',
        markers=True,
        text='icon',  # 그래프 위에 날씨 아이콘 표시
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
        ),
        clickmode='event+select'  # 클릭 이벤트 활성화
    )

    # st.plotly_chart에 on_select="rerun" 속성을 주어 클릭 이벤트를 감지합니다.
    selected_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    # 5. 그래프 클릭 이벤트 처리 (팝업 트리거)
    if selected_data and "points" in selected_data.get("selection", {}) and selected_data["selection"]["points"]:
        # 클릭한 지점의 날짜 정보 가져오기
        clicked_point = selected_data["selection"]["points"][0]
        clicked_date_str = clicked_point.get("x")

        if clicked_date_str:
            # 클릭된 날짜와 일치하는 데이터프레임 행 찾기
            matched_rows = df[df['date'].dt.strftime('%Y-%m-%d') == clicked_date_str]
            if not matched_rows.empty:
                # 첫 번째 매칭된 데이터를 팝업 함수로 전달
                show_diary_popup(matched_rows.iloc[0])

    # 6. 하단 데이터 표
    with st.expander("상세 기록 보기"):
        st.dataframe(df[['date', 'emotion', 'score', 'content']].rename(
            columns={'date': '날짜', 'emotion': '감정', 'score': '점수', 'content': '내용'}
        ))
else:
    st.info("아직 기록된 일기가 없습니다. 'Emotional Diary' 페이지에서 첫 일기를 써보세요!")
