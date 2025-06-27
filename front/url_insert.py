import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Webtoon, WebtoonGroup, Episode
from sqlalchemy import or_
from function import save_cut_images_from_episode
from PIL import Image
import os
import requests
from io import BytesIO
import sqlalchemy.exc
from function.code_label import GENRE_MAP, GENRE_LABEL_TO_CODE

def show():
    st.header("🕸 웹툰 URL 저장")

    session = SessionLocal()

    # 1. 웹툰 검색
    search_title = st.text_input("🔍 URL 등록할 웹툰 검색", placeholder="예: 화산귀환, 전지적 독자 시점 등")
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

                # 2. 한글 웹툰 등록
                new_webtoon = Webtoon(
                    title=new_title,
                    company=new_company,
                    genre=GENRE_LABEL_TO_CODE[genre_label],
                    url=new_url,
                    language="kr",
                )
                session.add(new_webtoon)
                session.commit()
                st.success("✅ 한글 웹툰이 등록되었습니다. 화면을 새로 고침 해주세요.")
                session.close()
                return
            
    elif selected_webtoon.group_id is None:
        # 영어 웹툰 추가 확장 영역
        with st.expander("🆕 영어 웹툰 추가"):
            new_title_en = st.text_input("영어 웹툰 제목")
            new_url_en = st.text_input("영어 웹툰 URL")

            if st.button("영어 웹툰 등록"):
                # 1. 웹툰 그룹 생성
                group_name = selected_webtoon.title + " / " + new_title_en
                new_group = WebtoonGroup(group_name=group_name)
                session.add(new_group)
                session.commit()
                session.refresh(new_group)

                # 2. 영어 웹툰 생성
                new_webtoon_en = Webtoon(
                    title=new_title_en,
                    company=selected_webtoon.company,
                    genre=selected_webtoon.genre,
                    url=new_url_en,
                    language="en",
                    group_id=new_group.id
                )
                session.add(new_webtoon_en)

                # 3. 선택된 한글 웹툰에도 group_id 할당
                selected_webtoon.group_id = new_group.id
                session.add(selected_webtoon)

                # 4. 커밋
                session.commit()

                st.success("✅ 영어 웹툰과 그룹 연결이 완료되었습니다.")

    # 3. 에피소드 및 컷 이미지 등록
    if selected_webtoon:
        st.subheader("🌐 한글 웹툰 에피소드 입력")
        episode_url = st.text_input("에피소드 URL 등록하기 (한글)", key="kr_url")
        episode_number_input = st.number_input("에피소드 회차 등록하기", 1, key="kr_episode_num")

        if episode_url:
            episode = session.query(Episode).filter_by(
                webtoon_id=selected_webtoon.id,
                url=episode_url,
                lang="kr"
            ).first()

            jpg_base_url = ""

            if episode is None:
                jpg_base_url = st.text_input("컷 이미지 경로 입력 (_IMAG01_1.jpg 형태)", key="kr_jpg_url")
                if jpg_base_url:
                    try:
                        new_ep = Episode(
                            webtoon_id=selected_webtoon.id,
                            episode_number=episode_number_input,
                            lang="kr",
                            url=episode_url,
                            jpg_url=jpg_base_url
                        )
                        session.add(new_ep)
                        session.commit()
                        st.success("✅ 한글 에피소드 등록 완료!")
                        episode = new_ep
                    except sqlalchemy.exc.SQLAlchemyError as e:
                        session.rollback()
                        st.error("❌ DB 등록 중 오류 발생 (한글)")
                        st.exception(e)
            else:
                jpg_base_url = episode.jpg_url

        if selected_webtoon.group_id:
            # ✨ 영어 웹툰 에피소드 입력
            st.subheader("🌎 영어 웹툰 에피소드 입력")
            episode_url_en = st.text_input("에피소드 URL 등록하기 (영어)", key="en_url")
            cut_size_en = st.number_input("캡처시 상단 자르는 범위 px단위", value=50)

            if episode_url_en:
                episode_en = session.query(Episode).filter_by(
                    webtoon_id=selected_webtoon.id,
                    url=episode_url_en,
                    lang="en"
                ).first()

                if episode_en is None:
                    if st.button("영어 에피소드 등록"):
                        try:
                            new_ep_en = Episode(
                                webtoon_id=selected_webtoon.id,
                                episode_number=episode_number_input,
                                lang="en",
                                url=episode_url_en,
                                jpg_url=None,  # 영어는 jpg URL 없음
                                cut_size = cut_size_en
                            )
                            session.add(new_ep_en)
                            session.commit()
                            st.success("✅ 영어 에피소드 등록 완료!")
                        except sqlalchemy.exc.SQLAlchemyError as e:
                            session.rollback()
                            st.error("❌ DB 등록 중 오류 발생 (영어)")
                            st.exception(e)
                else:
                    st.info("이미 등록된 영어 에피소드입니다.")

        session.close()
