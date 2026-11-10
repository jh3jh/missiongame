import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 기본 설정 (귀여운 아이콘과 제목)
st.set_page_config(page_title="미션 보물 찾기", layout="centered", page_icon="🧸")

# 2. 아기자기한 디자인을 위한 커스텀 CSS (주아체 폰트, 색상, 애니메이션)
st.markdown("""
    <style>
    /* 귀여운 폰트(배달의민족 주아체) 적용 */
    @import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Jua', sans-serif !important;
    }
    
    /* 배경은 솜사탕 같은 연한 파스텔 핑크, 글자는 부드러운 차콜색 */
    .stApp {
        background-color: #fff0f5; 
    }
    h1, h2, h3, p, div {
        color: #334155 !important;
    }

    /* 제비뽑기 물음표 박스 콩콩 뛰는 애니메이션 */
    @keyframes bounce-shake {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-15px) rotate(-5deg); }
        50% { transform: translateY(0) rotate(5deg); }
        75% { transform: translateY(-15px) rotate(-5deg); }
    }
    .shake-box {
        font-size: 110px;
        text-align: center;
        animation: bounce-shake 0.4s infinite;
        margin: 30px 0;
        text-shadow: 3px 3px 10px rgba(0,0,0,0.1);
    }

    /* 미션 텍스트 강조 (알록달록 점선 테두리와 둥근 모서리) */
    .mission-text {
        font-size: 45px;
        text-align: center;
        background-color: #ffffff;
        padding: 40px;
        border-radius: 30px;
        border: 5px dashed #a78bfa; /* 파스텔 보라색 점선 */
        margin: 20px 0;
        color: #1e3a8a !important; /* 미션 글씨는 돋보이는 네이비 */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        line-height: 1.4;
    }

    /* 버튼 공통 스타일 (둥글고 귀엽게) */
    div[data-testid="stButton"] > button {
        border-radius: 25px !important;
        font-size: 22px !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05) !important;
    }

    /* O 성공 버튼 (Primary) -> 파스텔 그린 */
    div[data-testid="baseButton-primary"] {
        background-color: #bbf7d0 !important; 
        border: 2px solid #86efac !important;
        color: #14532d !important;
    }

    /* X 실패 버튼 및 일반 버튼 (Secondary) -> 파스텔 핑크 */
    div[data-testid="baseButton-secondary"] {
        background-color: #fbcfe8 !important; 
        border: 2px solid #f9a8d4 !important;
        color: #831843 !important;
    }
    
    /* 탭 디자인 귀엽게 수정 */
    button[data-baseweb="tab"] {
        font-size: 20px !important;
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 세션 상태 초기화
if 'groups' not in st.session_state:
    st.session_state.groups = {}
if 'missions' not in st.session_state:
    st.session_state.missions = []
if 'current_mission' not in st.session_state:
    st.session_state.current_mission = None
if 'current_group' not in st.session_state:
    st.session_state.current_group = None

# 메인 타이틀
st.markdown("<h1 style='text-align: center; font-size: 55px; color: #db2777 !important;'>🧸 미션 보물 찾기 🧸</h1>", unsafe_allow_html=True)

# 사이드바 (설정 및 현황판)
with st.sidebar:
    st.header("📂 쉿, 선생님 전용 공간")
    uploaded_file = st.file_uploader("미션 목록 엑셀(.xlsx) 업로드", type=['xlsx', 'csv'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.missions = df.iloc[:, 0].dropna().astype(str).tolist()
            st.success(f"✨ 미션 {len(st.session_state.missions)}개 쏙쏙 들어왔어요!")
        except Exception as e:
            st.error("파일을 읽지 못했어요. 첫 번째 열(A열)에 미션을 적어주세요.")

    st.divider()
    st.subheader("🏆 우리 반 실시간 순위")
    if st.session_state.groups:
        sorted_groups = sorted(st.session_state.groups.items(), key=lambda x: x[1], reverse=True)
        df_scores = pd.DataFrame(sorted_groups, columns=["모둠 팡팡!", "성공 별(점)"])
        df_scores.index = range(1, len(df_scores) + 1)
        st.dataframe(df_scores, use_container_width=True)
    else:
        st.info("아직 도착한 모둠이 없어요.")

# 4. 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 모둠 적기", "🎁 상자 열기", "🎉 파티 시간"])

# --- [탭 1] 모둠 설정 ---
with tab1:
    st.subheader("새로운 모둠이 도착했어요!")
    col1, col2 = st.columns([3, 1])
    with col1:
        new_group = st.text_input("모둠 이름 (예: 귀염둥이 1조)", key="group_input")
    with col2:
        st.write("")
        st.write("")
        if st.button("➕ 쏘옥 추가!", use_container_width=True):
            if new_group and new_group not in st.session_state.groups:
                st.session_state.groups[new_group] = 0
                st.rerun()
            elif new_group in st.session_state.groups:
                st.warning("앗! 이미 있는 이름이에요.")

    if st.session_state.groups:
        st.write("🎈 지금 모인 친구들:")
        for g in list(st.session_state.groups.keys()):
            col_a, col_b = st.columns([4, 1])
            col_a.markdown(f"**{g}**")
            if col_b.button("빼기", key=f"del_{g}"):
                del st.session_state.groups[g]
                st.rerun()

# --- [탭 2] 미션 뽑기 및 판정 ---
with tab2:
    if not st.session_state.groups:
        st.warning("왼쪽 탭에서 모둠을 먼저 적어주세요! 📝")
    elif not st.session_state.missions:
        st.warning("왼쪽 서랍(사이드바)에 미션 엑셀을 넣어주세요! 📂")
    else:
        st.subheader("두근두근 미션 뽑기 🎲")
        selected_group = st.selectbox("어느 모둠이 상자를 열어볼까요?", list(st.session_state.groups.keys()))
        
        if st.button("✨ 물음표 상자 열기! ✨", use_container_width=True):
            st.session_state.current_group = selected_group
            st.session_state.current_mission = None
            
            # 흔들리는 물음표 상자 애니메이션
            placeholder = st.empty()
            placeholder.markdown("<div class='shake-box'>❔📦❔</div>", unsafe_allow_html=True)
            time.sleep(2) # 2초 동안 긴장감
            placeholder.empty() 
            
            st.session_state.current_mission = random.choice(st.session_state.missions)
            st.rerun()

        # 미션 화면
        if st.session_state.current_mission:
            st.markdown(f"<h3 style='text-align:center;'>도전: <span style='color:#ec4899;'>{st.session_state.current_group}</span></h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='mission-text'>{st.session_state.current_mission}</div>", unsafe_allow_html=True)
            
            col_o, col_x = st.columns(2)
            with col_o:
                # 성공 버튼 (type="primary" 속성으로 그린색 적용)
                if st.button("⭕ 완벽하게 성공!", use_container_width=True, type="primary"):
                    st.session_state.groups[st.session_state.current_group] += 1
                    st.session_state.current_mission = None
                    st.success("대단해요! 점수가 쑥쑥 올랐어요. 🌟")
                    time.sleep(1)
                    st.rerun()
            with col_x:
                # 실패 버튼 (일반 버튼으로 핑크색 적용)
                if st.button("❌ 앗, 실패...", use_container_width=True):
                    st.session_state.current_mission = None
                    st.error("아쉽지만 다음 기회에! 화이팅 🎈")
                    time.sleep(1)
                    st.rerun()

# --- [탭 3] 최종 결과 ---
with tab3:
    st.subheader("최종 순위 발표 🎊")
    if not st.session_state.groups:
        st.info("아직 게임이 시작되지 않았어요.")
    else:
        if st.button("👑 우승팀 보러가기 👑", use_container_width=True):
            max_score = max(st.session_state.groups.values())
            winners = [g for g, score in st.session_state.groups.items() if score == max_score]
            
            st.balloons() # 폭죽 대신 귀여운 풍선 파티클
            
            st.markdown("<h2 style='text-align: center; color: #8b5cf6 !important;'>오늘의 주인공은?</h2>", unsafe_allow_html=True)
            winners_str = ", ".join(winners)
            st.markdown(f"<h1 style='text-align: center; font-size: 70px; color: #ec4899 !important;'>💖 {winners_str} 💖</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>별을 무려 {max_score}개나 모았어요!</h3>", unsafe_allow_html=True)
            
            st.divider()
            st.write("참여한 모든 친구들 정말 멋져요!")
            sorted_groups = sorted(st.session_state.groups.items(), key=lambda x: x[1], reverse=True)
            for i, (g, score) in enumerate(sorted_groups, 1):
                st.markdown(f"**{i}등:** {g} ({score}개)")
