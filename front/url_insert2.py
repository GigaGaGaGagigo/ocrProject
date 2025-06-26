import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Webtoon, WebtoonGroup, Episode, CutImage
from sqlalchemy import or_
from function import save_cut_images_from_episode
from PIL import Image
import os
import requests
from io import BytesIO
import sqlalchemy.exc

# 장르 코드 ↔ 명칭 매핑
GENRE_MAP = {
    0: "액션",
    1: "로맨스",
    2: "스릴러",
    3: "무협"
}
GENRE_LABEL_TO_CODE = {v: k for k, v in GENRE_MAP.items()}

def show():
    st.header("🕸 웹툰 크롤링 + 이미지 저장")

    session = SessionLocal()

    # 1. 웹툰 검색
    search_title = st.text_input("🔍 크롤링할 웹툰 검색", placeholder="예: 화산귀환, 전지적 독자 시점 등")
    selected_webtoon = None

    if search_title:
        results = session.query(Webtoon).filter(
            or_(
                Webtoon.title.like(f"%{search_title}%"),
                Webtoon.title == search_title
            ),
            Webtoon.language == "kr"
        ).all()

        if results:
            titles = [f"{w.title} ({GENRE_MAP.get(w.genre, '미지정')})" for w in results]
            selected = st.selectbox("📚 검색 결과에서 선택", titles)
            selected_webtoon = results[titles.index(selected)]
        else:
            st.warning("검색 결과가 없습니다. 아래에서 새로 추가할 수 있습니다.")

    # 2. 웹툰 직접 추가
    if selected_webtoon is None:
        with st.expander("🆕 새 웹툰 추가"):
            new_title = st.text_input("제목")
            new_company = st.text_input("회사/출판사", value="Naver")
            genre_label = st.selectbox("장르", list(GENRE_LABEL_TO_CODE.keys()))
            new_url = st.text_input("웹툰 URL 입력")

            if st.button("웹툰 등록"):
                # 1. 웹툰 그룹 생성
                group_name = new_title  # 기본은 한글 제목과 동일하게
                new_group = WebtoonGroup(group_name=group_name)
                session.add(new_group)
                session.commit()
                session.refresh(new_group)

                # 2. 한글 웹툰 등록
                new_webtoon = Webtoon(
                    title=new_title,
                    company=new_company,
                    genre=GENRE_LABEL_TO_CODE[genre_label],
                    url=new_url,
                    language="kr",
                    group_id=new_group.id
                )
                session.add(new_webtoon)
                session.commit()
                st.success("✅ 한글 웹툰이 등록되었습니다. 화면을 새로 고침 해주세요.")

                # 3. 영어 웹툰 추가 확장 영역
                with st.expander("🆕 영어 웹툰 추가"):
                    new_title_en = st.text_input("영어 웹툰 제목")
                    new_company_en = st.text_input("영어 웹툰 회사/출판사", value="Naver")
                    genre_label_en = st.selectbox("장르 (영어 웹툰)", list(GENRE_LABEL_TO_CODE.keys()), key="genre_en")
                    new_url_en = st.text_input("영어 웹툰 URL")

                    if st.button("영어 웹툰 등록"):
                        new_webtoon_en = Webtoon(
                            title=new_title_en,
                            company=new_company_en,
                            genre=GENRE_LABEL_TO_CODE[genre_label_en],
                            url=new_url_en,
                            language="en",
                            group_id=new_group.id
                        )
                        session.add(new_webtoon_en)
                        session.commit()
                        st.success("✅ 영어 웹툰이 등록되었습니다.")

                session.close()
                return
       

    # 3. 에피소드 및 컷 이미지 등록
    if selected_webtoon:
        st.subheader("🌐 한글 웹툰 에피소드 입력")
        episode_url = st.text_input("에피소드 URL 등록하기", "")

        if episode_url:
            episode = session.query(Episode).filter_by(
                webtoon_id=selected_webtoon.id,
                url=episode_url
            ).first()

            jpg_base_url = ""

            if episode is None:
                jpg_base_url = st.text_input("컷 이미지 경로 입력 (_IMAG01_1.jpg 형태)")
                if jpg_base_url:
                        try:
                            new_ep = Episode(
                                webtoon_id=selected_webtoon.id,
                                episode_number=1,
                                lang='kr',
                                url=episode_url,
                                jpg_url=jpg_base_url
                            )
                            session.add(new_ep)
                            session.commit()
                            st.success("✅ 에피소드 등록 완료!")
                            episode = new_ep  # 이후 로직에서도 활용 가능하게 저장
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            session.rollback()
                            st.error("❌ DB 등록 중 오류 발생!")
                            st.exception(e)  # 콘솔 및 UI에 예외 전체 내용 출력
            else:
                jpg_base_url = episode.jpg_url          
    session.close()
