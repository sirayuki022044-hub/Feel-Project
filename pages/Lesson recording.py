import streamlit as st
import datetime
from supabase import create_client, Client

# ----------------------------------------------------------------
# ⚠️ 정미 선생님의 실제 Supabase 정보로 완벽 세팅
# ----------------------------------------------------------------
# 주소 끝에 공백이나 마침표가 들어가지 않도록 정확히 입력합니다.
SUPABASE_URL = "https://badsgkosnlrxbaubuowd.supabase.co"

# 아까 찾으신 sb_publishable_fHuK1... 로 시작하는 긴 anon key를 따옴표 사이에 넣어주세요.
SUPABASE_KEY = "sb_publishable_fHuK1bwD1LdwopIAcL9B_Q_D8tFYAtJ"

@st.cache_resource
def init_supabase():
    # 주소 앞뒤 공백을 자동으로 제거해 주는 .strip()을 붙여 안전장치를 합니다.
    return create_client(SUPABASE_URL.strip(), SUPABASE_KEY.strip())

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error(f"Supabase 초기화 실패 (주소나 키 형식 오류): {e}")

# ----------------------------------------------------------------
# 앱 제목 및 탭 설정
# ----------------------------------------------------------------
st.title("🏫 학습도움1실 수업 & 산출물 아카이브")
st.markdown("---")

tab1, tab2 = st.tabs(["📝 수업 기록하기", "🎨 디지털 산출물 보관소"])

# ----------------------------------------------------------------
# TAB 1: 수업 기록하기 (Supabase 연동 완료)
# ----------------------------------------------------------------
with tab1:
    st.header("오늘의 수업 기록")

    # 1. 수업 기록 입력 폼
    with st.form("class_log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            class_date = st.date_input("날짜", datetime.date.today())
        with col2:
            subject = st.text_input("과목/단원명", placeholder="예: AI와 함께하는 소셜미디어")

        activity = st.text_area("주요 수업 내용 및 피드백", placeholder="오늘 수업의 핵심 활동이나 학생 반응을 기록하세요.")

        submit_btn = st.form_submit_button("수업 기록 저장하기")

        if submit_btn:
            if not subject or not activity:
                st.error("과목명과 수업 내용을 모두 입력해주세요.")
            else:
                with st.spinner("데이터베이스에 수업 기록을 저장 중입니다..."):
                    try:
                        log_data = {
                            "class_date": class_date.isoformat(),
                            "subject": subject,
                            "activity": activity
                        }
                        # 'class_logs' 테이블에 데이터 저장
                        supabase.table("class_logs").insert(log_data).execute()
                        st.success(f"✅ {class_date} [{subject}] 수업 기록이 완료되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"수업 기록 저장 실패: {e}")

    st.markdown("---")

    # 2. 저장된 수업 기록 실시간 출력
    st.subheader("📋 지난 수업 기록 목록")
    try:
        log_response = supabase.table("class_logs").select("*").order("class_date", desc=True).execute()
        logs = log_response.data

        if not logs:
            st.info("아직 기록된 수업이 없습니다. 오늘의 첫 수업을 기록해 보세요!")
        else:
            for log in logs:
                with st.container(border=True):
                    st.markdown(f"### 📖 {log['subject']}")
                    st.caption(f"📅 **수업일**: {log['class_date']}")
                    st.write(log['activity'])
    except Exception as e:
        st.error(f"수업 기록을 불러오는 중 오류가 발생했습니다: {e}")

# ----------------------------------------------------------------
# TAB 2: 디지털 산출물 보관소
# ----------------------------------------------------------------
with tab2:
    st.header("제작 산출물 및 과제 보관")
    st.caption("링크를 공유하거나, 학생들이 제출한 과제 사진 및 PDF 파일을 직접 업로드하세요.")

    # 새 산출물 등록 기능
    with st.expander("➕ 새 산출물/과제 등록하기", expanded=False):
        tool_name = st.selectbox("구분/툴 선택", ["Canva", "Padlet", "Tooning", "과제 사진(JPG/PNG)", "과제 PDF", "기타"])
        project_title = st.text_input("프로젝트/과제명", placeholder="예: 우리 반 감정 동화책 만들기")

        uploaded_file = st.file_uploader("과제 사진 또는 PDF 파일 업로드", type=["png", "jpg", "jpeg", "pdf"])
        project_url = st.text_input("링크 URL (선택사항)", placeholder="https://...")
        project_desc = st.text_area("설명 및 피드백")

        add_btn = st.button("Supabase에 저장하기")

        if add_btn:
            if not project_title:
                st.error("프로젝트/과제명을 입력해주세요.")
            else:
                final_url = project_url

                if uploaded_file is not None:
                    with st.spinner("Supabase 스토리지에 파일을 업로드 중입니다..."):
                        try:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                            file_path = f"{timestamp}_{uploaded_file.name}"
                            file_data = uploaded_file.read()

                            supabase.storage.from_("student-artifacts").upload(
                                path=file_path,
                                file=file_data,
                                file_options={"content-type": uploaded_file.type}
                            )
                            final_url = supabase.storage.from_("student-artifacts").get_public_url(file_path)
                            st.success("📁 파일이 Supabase 스토리지에 안전하게 저장되었습니다!")
                        except Exception as e:
                            st.error(f"스토리지 업로드 실패: {e}")
                            st.stop()

                with st.spinner("데이터베이스에 정보를 기록 중입니다..."):
                    try:
                        data = {
                            "tool_name": tool_name,
                            "project_title": project_title,
                            "file_or_link_url": final_url,
                            "description": project_desc,
                            "created_at": datetime.datetime.now().isoformat()
                        }
                        supabase.table("artifacts").insert(data).execute()
                        st.success(f"🎉 [{project_title}] 아카이브 등록이 최종 완료되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"데이터베이스 저장 실패: {e}")

    st.markdown("---")

    # 실시간 산출물 목록 출력
    st.subheader("📚 실시간 산출물 & 과제 아카이브 목록")
    try:
        response = supabase.table("artifacts").select("*").order("created_at", desc=True).execute()
        items = response.data

        if not items:
            st.info("아직 등록된 산출물이 없습니다.")
        else:
            col_a, col_b = st.columns(2)
            for index, item in enumerate(items):
                target_col = col_a if index % 2 == 0 else col_b
                with target_col:
                    with st.container(border=True):
                        st.markdown(f"### 📘 {item['project_title']}")
                        date_str = item['created_at'][:10] if item['created_at'] else "날짜 불명"
                        st.caption(f"**툴**: {item['tool_name']} | **등록일**: {date_str}")

                        if item['description']:
                            st.write(item['description'])

                        if item['file_or_link_url']:
                            if "padlet.com" in item['file_or_link_url'].lower():
                                st.components.v1.iframe(item['file_or_link_url'], height=250, scrolling=True)
                            elif any(ext in item['file_or_link_url'].lower() for ext in [".png", ".jpg", ".jpeg"]):
                                st.image(item['file_or_link_url'], use_container_width=True)

                            st.link_button("📄 작품/파일 열기", item['file_or_link_url'], use_container_width=True)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
