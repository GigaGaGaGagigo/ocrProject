# front/ocr_admin_eval.py
import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Episode, Webtoon
from front.use_home import webtoon_read

def show():
    st.title("🛠️ OCR 관리자 분석 페이지")
    st.markdown("웹툰 컷을 직접 확인하고 대사 인식 결과를 점검할 수 있습니다.")

    session = SessionLocal()

    # 📘 한글 에피소드 불러오기
    kr_episodes = session.query(Episode).filter_by(lang="kr").order_by(Episode.episode_number).all()

    if not kr_episodes:
        st.warning("한글 웹툰 에피소드가 없습니다.")
        session.close()
        return

    # 👉 에피소드에 해당하는 웹툰 제목을 별도로 조회
    episode_titles = []
    for ep in kr_episodes:
        webtoon = session.query(Webtoon).get(ep.webtoon_id)
        episode_titles.append(f"{webtoon.title} - {ep.episode_number}화")

    selected_index = st.selectbox("🇰🇷 평가할 회차를 선택하세요", range(len(kr_episodes)), format_func=lambda i: episode_titles[i])
    selected_kr_ep = kr_episodes[selected_index]

    # 📕 영어 에피소드 매칭
    selected_en_ep = session.query(Episode).filter_by(
        webtoon_id=selected_kr_ep.webtoon_id,
        episode_number=selected_kr_ep.episode_number,
        lang="en"
    ).first()

    session.close()

    if selected_en_ep:
        webtoon_read(selected_kr_ep, selected_en_ep)
    else:
        st.warning("❌ 해당 회차의 영어 에피소드가 없습니다.")