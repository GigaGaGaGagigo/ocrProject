import streamlit as st
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.crawl_sql import Webtoon

def show():
    st.title("🇰🇷 웹툰 선택")

    # DB 세션 생성
    db: Session = SessionLocal()

    # 웹툰 목록 조회 (KR 언어만)
    kr_webtoons = db.query(Webtoon).filter(Webtoon.language == 'kr').all()

    if kr_webtoons:
        titles = [f"{w.title} (ID: {w.id})" for w in kr_webtoons]
        selected = st.selectbox("웹툰을 선택하세요:", titles)

        selected_index = titles.index(selected)
        selected_webtoon = kr_webtoons[selected_index]

        st.markdown(f"### 🔗 웹툰 링크")
        st.markdown(f"[{selected_webtoon.title}]({selected_webtoon.url})")

    else:
        st.warning("KR 언어 웹툰이 없습니다.")