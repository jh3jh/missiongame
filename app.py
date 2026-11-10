import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 기본 설정 (가독성 높은 제목과 파스텔톤 커스텀 CSS)
st.set_page_config(page_title="미션 보물 찾기", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경 파스텔 핑크톤, 글자는 진한 네이비(가독성 확보) */
    .stApp {
        background-color: #fdf2f8;
        color: #1e293b;
    }
    h1, h2, h3, p, div {
        color: #1e293b !important;
    }
    /* 제비뽑기 애니메이션 (흔들리는 효과) */
    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        20% { transform: translate(-3px, 0px) rotate(1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        40% { transform: translate(1px, -1px) rotate(1deg); }
        50% { transform: translate(-1px, 2px) rotate(-1deg); }
        60% { transform: translate(-3px, 1px) rotate(0deg); }
        70% { transform: translate(3px, 1px) rotate(-1deg); }
        80% { transform: translate(-1px, -1px) rotate(1deg); }
        90% { transform: translate(1px, 2px) rotate(0deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    .shake-box {
        font-size: 100px;
        text-align: center;
        animation: shake 0.5s infinite;
        margin: 20px 0;
    }
    /* 미션 텍스트 강조 */
    .mission-text {
        font-size: 40px;
        font-weight: 900;
        text-align: center;
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        border: 4px solid #93c5fd; /* 파스텔 블루 테두리 */
        margin: 20px 0;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 상태(Session State) 초기화 (새로고침해도 데이터 유지)
if 'groups' not in st.session_state:
    st.session_state.groups = {}  # {'1모둠': 0, '2모둠': 0, ...}
if 'missions' not in st.session_state:
    st.session_state.missions = []
if 'current_mission' not in st.session_state:
    st.session_state.current_mission = None
if 'current_group' not in st.session_state:
    st.session_state.current_group = None
if 'drawing' not in st.session_state:
    st.session_state.drawing = False

# 메인 타이틀
st.markdown("<h1 style='text-align: center; font-size: 50px;'>✨ 미션 보물 찾기 ✨</h1>", unsafe_allow_html=True)

# 3. 사이드바: 엑셀 미션 업로드 및 현황판
with st.sidebar:
    st.header("📂 설정 및 현황판")
    uploaded_file = st.file_uploader("미션 목록 업로드 (엑셀 파일)", type=['xlsx', 'csv'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            # 첫 번째 열의 데이터를 미션 목록으로 가져옴
            st.session_state.missions = df.iloc[:, 0].dropna().astype(str).tolist()
            st.success(f"미션 {len(st.session_state.missions)}개 로드 완료!")
        except Exception as e:
            st.error("파일을 읽는 중 오류가 발생했습니다. 첫 번째 열에 미션을 작성해주세요.")

    st.divider()
    st.subheader("🏆 실시간 모둠 현황")
    if st.session_state.groups:
        # 점수 순으로 정렬하여 표 형태로 표시
        sorted_groups = sorted(st.session_state.groups.items(), key=lambda x: x[1], reverse=True)
        df_scores = pd.DataFrame(sorted_groups, columns=["모둠명", "성공 횟수(점)"])
        df_scores.index = range(1, len(df_scores) + 1)
        st.dataframe(df_scores, use_container_width=True)
    else:
        st.info("아직 등록된 모둠이 없습니다.")

# 4. 모둠 추가 탭 / 메인 게임 탭 분리
tab1, tab2, tab3 = st.tabs(["👥 모둠 설정", "🎁 미션 뽑기 및 판정", "🎉 최종 결과"])

# --- [탭 1] 모둠 설정 ---
with tab1:
    st.subheader("모둠 추가하기")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_group = st.text_input("모둠 이름 입력 (예: 1모둠, 지혜네 조)", key="group_input")
    with col2:
        st.write("") # 줄맞춤용
        st.write("")
        if st.button("➕ 추가하기", use_container_width=True):
            if new_group and new_group not in st.session_state.groups:
                st.session_state.groups[new_group] = 0
                st.rerun()
            elif new_group in st.session_state.groups:
                st.warning("이미 존재하는 모둠입니다.")

    if st.session_state.groups:
        st.write("현재 참가 모둠:")
        for g in list(st.session_state.groups.keys()):
            col_a, col_b = st.columns([4, 1])
            col_a.markdown(f"**{g}**")
            if col_b.button("삭제", key=f"del_{g}"):
                del st.session_state.groups[g]
                st.rerun()

# --- [탭 2] 미션 뽑기 및 판정 ---
with tab2:
    if not st.session_state.groups:
        st.warning("모둠 설정 탭에서 모둠을 먼저 추가해주세요.")
    elif not st.session_state.missions:
        st.warning("사이드바에서 미션 엑셀 파일을 업로드해주세요.")
    else:
        st.subheader("제비뽑기")
        selected_group = st.selectbox("어느 모둠이 뽑나요?", list(st.session_state.groups.keys()))
        
        if st.button("🎲 미션 제비뽑기 시작!", use_container_width=True):
            st.session_state.current_group = selected_group
            st.session_state.current_mission = None
            
            # 흔들리는 항아리 애니메이션 효과 (st.empty() 활용)
            placeholder = st.empty()
            placeholder.markdown("<div class='shake-box'>🍯</div>", unsafe_allow_html=True)
            time.sleep(2) # 2초간 긴장감 조성
            placeholder.empty() # 항아리 지우기
            
            # 랜덤 미션 배정
            st.session_state.current_mission = random.choice(st.session_state.missions)
            st.rerun()

        # 미션이 뽑혔을 때 화면에 크게 표시하고 O/X 버튼 제공
        if st.session_state.current_mission:
            st.markdown(f"<h3 style='text-align:center;'>도전 모둠: <span style='color:#3b82f6;'>{st.session_state.current_group}</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='mission-text'>{st.session_state.current_mission}</div>", unsafe_allow_html=True)
            
            col_o, col_x = st.columns(2)
            with col_o:
                if st.button("⭕ 성공 (점수 획득)", use_container_width=True, type="primary"):
                    st.session_state.groups[st.session_state.current_group] += 1
                    st.session_state.current_mission = None
                    st.success("미션 성공! 점수가 기록되었습니다.")
                    time.sleep(1)
                    st.rerun()
            with col_x:
                if st.button("❌ 실패", use_container_width=True):
                    st.session_state.current_mission = None
                    st.error("앗, 실패! 다음 기회를 노려보세요.")
                    time.sleep(1)
                    st.rerun()

# --- [탭 3] 최종 결과 ---
with tab3:
    st.subheader("최종 순위 및 우승팀 확인")
    if not st.session_state.groups:
        st.info("아직 게임이 시작되지 않았습니다.")
    else:
        if st.button("🎊 게임 종료 및 결과 보기 🎊", use_container_width=True):
            # 가장 점수가 높은 팀 찾기
            max_score = max(st.session_state.groups.values())
            winners = [g for g, score in st.session_state.groups.items() if score == max_score]
            
            st.balloons() # 스트림릿 내장 폭죽 파티클 애니메이션
            
            st.markdown("<h2 style='text-align: center; color: #64748b;'>영광의 우승팀</h2>", unsafe_allow_html=True)
            winners_str = ", ".join(winners)
            st.markdown(f"<h1 style='text-align: center; font-size: 60px; color: #ec4899;'>👑 {winners_str} 👑</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>최종 {max_score}점 달성!</h3>", unsafe_allow_html=True)
            
            st.divider()
            st.write("전체 결과 현황")
            sorted_groups = sorted(st.session_state.groups.items(), key=lambda x: x[1], reverse=True)
            for i, (g, score) in enumerate(sorted_groups, 1):
                st.markdown(f"**{i}위:** {g} ({score}점)")
