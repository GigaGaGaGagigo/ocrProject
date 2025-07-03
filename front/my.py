import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import WrongNote, Dialogue, RecentWebtoonView, Webtoon, Episode, CutImage
from front import use_home

def show():
    
    # 세션 상태 기본값 설정
    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword = ""
    if "selected_genre" not in st.session_state:
        st.session_state.selected_genre = "전체"
    if "selected_webtoon_id" not in st.session_state:
        st.session_state.selected_webtoon_id = None

    # ✅ 리더 모드 진입 시
    if st.session_state.get("view_mode") == "reader":
        selected_ep_kr = st.session_state["selected_ep_kr"]
        selected_ep_en = st.session_state.get("selected_ep_en")
        use_home.webtoon_read(selected_ep_kr, selected_ep_en)
        return
    
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
                session = SessionLocal()

                # 최신 5개 오답 불러오기
                wrong_notes = (
                    session.query(WrongNote)
                    .order_by(WrongNote.wrong_at.desc())
                    .limit(5)
                    .all()
                )

                if wrong_notes:
                    for i, note in enumerate(wrong_notes, start=1):
                        kr_d = session.query(Dialogue).filter_by(id=note.kr_dialogue_id).first()
                        en_d = session.query(Dialogue).filter_by(id=note.en_dialogue_id).first()

                        if kr_d and en_d:
                            # 버튼 클릭 감지용 key 생성
                            button_key = f"wrong_note_{i}"

                            # 버튼과 텍스트를 한 줄로 구성
                            cols = st.columns([1, 12])
                        with cols[0]:
                            if st.button(f"{i}", key=f"wrong_note_btn_{i}"):
                                st.session_state["view_mode"] = "reader"
                            
                                image_kr = session.query(CutImage).filter_by(
                                    id=kr_d.cut_image_id,
                                ).first()

                                st.session_state["cut_index"] = image_kr.cut_number

                                ep_kr = session.query(Episode).filter_by(
                                    id=image_kr.episode_id,
                                ).first()

                                st.session_state["selected_ep_kr"] = ep_kr

                                image_en = session.query(CutImage).filter_by(
                                    id=en_d.cut_image_id,
                                ).first()

                        
                                ep_en = session.query(Episode).filter_by(
                                    id=image_en.episode_id,
                                ).first()

                                st.session_state["selected_ep_en"] = ep_en

                                st.session_state["reader_rendered"] = False
                                st.rerun()

                            # 버튼 스타일을 텍스트처럼 보이게 하기 위해 CSS 삽입
                            st.markdown("""
                                <style>
                                div[data-testid="stButton"] button {
                                    padding: 5px;
                                    font-size: 14px;
                                    color: black;
                                    border: none;
                                    box-shadow: none;
                                    cursor: pointer;
                                }
                                </style>
                            """, unsafe_allow_html=True)

                        with cols[1]:
                            st.write(f"**{en_d.content}** - {kr_d.content}")
                else:
                    st.info("✅ 최근 오답이 없습니다.")

        session.close()

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
                session = SessionLocal()
                recent = session.query(RecentWebtoonView)\
                    .filter_by(user_id="default")\
                    .order_by(RecentWebtoonView.view_at.desc())\
                    .first()

                if recent:
                    webtoon = session.query(Webtoon).get(recent.webtoon_id)
                    episode = session.query(Episode).get(recent.episode_id)

                    # 컷 수 가져오기
                    ep_total_cut = episode.cut_size if episode.cut_size else 20
                    progress = min(int((recent.last_cut_number / ep_total_cut) * 100), 100)

                    st.write(f"🖼️ 최근 본 웹툰: **{webtoon.title} - {episode.episode_number}화**")
                    st.write(f"🎬 마지막 컷: {recent.last_cut_number}번")
                    st.progress(progress, text="학습 진행률")

                    # 👉 클릭하면 바로 이어보기
                    if st.button("📖 이어서 보기"):


                        st.session_state["view_mode"] = "reader"
                        st.session_state["selected_ep_kr"] = episode
                        st.session_state["cut_index"] = recent.last_cut_number

                        # 영어 회차도 함께 불러오기
                        ep_en = session.query(Episode).filter_by(
                            webtoon_id=webtoon.id,
                            lang="en",
                            episode_number=episode.episode_number
                        ).first()
                        st.session_state["selected_ep_en"] = ep_en

                        # ✅ 플래그 초기화하고 rerun 호출
                        st.session_state["reader_rendered"] = False
                        st.rerun()
                else:
                    st.write("최근 본 웹툰이 없습니다.")
                session.close()

    # ▶️ 탭3: 제안 및 피드백
    with tab3:
        
        st.info("마이페이지는 계속 업데이트 중이에요! 원하는 기능이 있다면 아래에 제안해 주세요.")
        feedback = st.text_area("✍️ 기능 제안 또는 개선사항")
        if st.button("제출하기"):
            st.success("감사합니다! 소중한 의견은 개발팀에게 전달됩니다.")