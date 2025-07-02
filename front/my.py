import streamlit as st

def show():
    
    st.header("🏠 마이페이지")
    st.markdown("웹툰 기반 외국어 학습 플랫폼에 오신 걸 환영합니다 😊")
    st.markdown("---")

    # ✅ 탭 나누기
    tab2, tab3 = st.tabs(["학습 기록", "설정 / 제안"])

    # ▶️ 탭2: 학습 기록 및 미션
    with tab2:
        col3, col22 = st.columns(2)
        col12, col4 = st.columns(2)
        col5, col6 = st.columns(2)

        with col3:
            with st.expander("🎯 오늘의 학습 미션", expanded=True):
                st.write("✅ 웹툰 5컷 보기")
                st.write("✅ 한글-영어 문장 비교해보기")
                st.write("⬜ 단어 복습 3개")
                st.progress(0.66)

        with col22:
            with st.expander("📘 오답노트", expanded=True):
                st.write("1. **resolve** - 해결하다")
                st.write("2. **defeat** - 패배시키다")
                st.write("3. **clan** - 부족, 문파")
                if st.button("📤 단어장 내보내기"):
                    st.success("✅ 단어장이 다운로드되었습니다 (예시)")

        #col12, col4 = st.columns(2)

        with col12:
            with st.expander("📈 나의 학습 통계 보기"):
                st.write("총 학습 컷 수: 34컷")
                st.write("OCR 사용 횟수: 20회")
                st.write("정답률: 72%")
                st.line_chart([10, 15, 20, 22, 30, 34])

        with col4:
            with st.expander("🌟 오늘의 추천 웹툰"):
                st.write("📚 당신의 관심 장르: 무협, 액션")
                st.write("📊 최근 인기 웹툰 : 화산귀환",
                    caption="🔥 오늘의 추천: 화산귀환",
                    use_column_width=True
                )
                st.button("📖 지금 보러 가기")

        #col5, col6 = st.columns(2)
        with col5:
            with st.expander("⭐ 관심 웹툰"):
            
                favorites = st.multiselect(
                "좋아하는 웹툰을 선택하세요",
                ["유미의 세포들", "김부장", "화산귀환", "스릴러", "입학용병"]
            )
                st.selectbox("추천 장르 기반", ["살아야 죽는 남자", "입학용병", "무협", "참교육"])

        with col6:
            with st.expander("📅 최근 본 웹툰"):
                st.write("🖼️ 최근 본 웹툰: **화산귀환**")
                st.write("📍 마지막 컷: 12번")
                st.progress(60, text="학습 진행률")

    # ▶️ 탭3: 제안 및 피드백
    with tab3:
        
        st.info("마이페이지는 계속 업데이트 중이에요! 원하는 기능이 있다면 아래에 제안해 주세요.")
        feedback = st.text_area("✍️ 기능 제안 또는 개선사항")
        if st.button("제출하기"):
            st.success("감사합니다! 소중한 의견은 개발팀에게 전달됩니다.")