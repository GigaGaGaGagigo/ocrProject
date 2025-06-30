import streamlit as st

def show():
    st.header("🏠 마이페이지")
    st.markdown("웹툰 기반 외국어 학습 플랫폼에 오신 걸 환영합니다 😊")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # 📌 내 정보
    with col1:
        st.subheader("👤 내 정보")
        name = st.text_input("이름:", key="username")
        age = st.slider("나이", 10, 60, 20)
        goal = st.selectbox("학습 목표", ["일상 회화", "비즈니스 영어", "자격증 대비"])

    # 🎯 관심 웹툰
    with col2:
        st.subheader("⭐ 관심 웹툰")
        favorites = st.multiselect(
            "좋아하는 웹툰을 선택하세요",
            ["유미의 세포들", "김부장", "화산귀환", "스릴러", "입학용병"]
        )

    # 🕒 최근 활동
    with st.expander("📅 최근 본 웹툰"):
        st.write("🖼️ 최근 본 웹툰: **화산귀환**")
        st.write("📍 마지막 컷: 12번")
        st.progress(60, text="학습 진행률")

    # 📈 맞춤 분석
    with st.expander("📊 나의 학습 통계"):
        st.write("총 학습 컷 수: 34컷")
        st.write("OCR 결과 확인률: 80%")
        st.write("정답률: 72%")

    st.markdown("---")
    st.info("마이페이지는 계속 업데이트 중이에요! 원하는 기능이 있다면 아래에 제안해 주세요.")
    feedback = st.text_area("✍️ 기능 제안 또는 개선사항")
    if st.button("제출하기"):
        st.success("감사합니다! 소중한 의견은 개발팀에게 전달됩니다.")






    # ✅ 관심 목록
    st.subheader("🌟 관심 목록")
    favorite = st.multiselect(
        "관심 있는 웹툰을 선택하세요:",
        ["유미의 세포들", "김부장", "화산귀환", "스릴러", "입학용병", "무협"],
        default=["화산귀환"]
    )

    # ✅ 최근 본 웹툰
    st.subheader("🕓 최근 본 웹툰")
    recent = st.selectbox("가장 최근 본 웹툰", ["유미의 세포들", "김부장", "화산귀환", "스릴러"])

    # ✅ 나의 맞춤 정보
    st.subheader("🔍 나의 맞춤 정보")
    st.selectbox("추천 장르 기반", ["살아야 죽는 남자", "입학용병", "무협", "참교육"])

    st.markdown("---")

    # ✅ 학습 통계
    with st.expander("📈 나의 학습 통계 보기"):
        st.write("총 학습 컷 수: 34컷")
        st.write("OCR 사용 횟수: 20회")
        st.write("정답률: 72%")
        st.line_chart([10, 15, 20, 22, 30, 34])  # 예시: 컷 수 증가 추이

    # ✅ 단어장 / 오답노트
    with st.expander("📘 내 단어장 / 오답노트"):
        st.write("1. **resolve** - 해결하다")
        st.write("2. **defeat** - 패배시키다")
        st.write("3. **clan** - 부족, 문파")
        if st.button("📤 단어장 내보내기"):
            st.success("✅ 단어장이 다운로드되었습니다 (예시)")

    # ✅ 오늘의 학습 미션
    with st.expander("🎯 오늘의 학습 미션"):
        st.write("✅ 웹툰 5컷 보기")
        st.write("✅ OCR 결과 확인 1회")
        st.write("⬜ 단어 복습 3개")
        st.progress(0.66)

    # ✅ 오늘의 추천 웹툰
    with st.expander("🌟 오늘의 추천 웹툰"):
        st.write("📚 당신의 관심 장르: 무협, 액션")
        st.image("https://i.namu.wiki/i/lm1oG_RqkW7D6e6FGlw4gEjBObX1zqEdyr6fEDMEdbfdwJYyi10mGQkM5MCPM_dBtyVaUlZDN1OTeKymknToh7ZVrL4qWoPyoz4rlGKwWLhbiEVmBPSsMgAnff6Zc_Ux67XwlgMG4DY-Y_9akKmsow.webp", caption="🔥 오늘의 추천: 화산귀환")
        st.button("📖 지금 보러 가기")