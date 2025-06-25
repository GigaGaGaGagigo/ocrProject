import streamlit as st
from db.database import SessionLocal
from db.crawl_sql import Webtoon, Episode, CutImage
from sqlalchemy import or_
from function import save_cut_images_from_episode
from PIL import Image
import os
import requests
from io import BytesIO

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
                new_webtoon = Webtoon(
                    title=new_title,
                    company=new_company,
                    genre=GENRE_LABEL_TO_CODE[genre_label],
                    url=new_url,
                    language="kr"
                )
                session.add(new_webtoon)
                session.commit()
                st.success("✅ 웹툰이 등록되었습니다. 페이지를 새로고침 해주세요.")
                session.close()
                return

    # 3. 에피소드 및 컷 이미지 등록
    if selected_webtoon:
        st.subheader("🌐 한글 웹툰 에피소드 입력")
        episode_url = st.text_input("에피소드 URL 입력", value=selected_webtoon.url or "")

        episode = session.query(Episode).filter_by(
            webtoon_id=selected_webtoon.id,
            url=episode_url,
            lang='kr'
        ).first()

        jpg_base_url = ""

        if not episode and episode_url:
            jpg_base_url = st.text_input("컷 이미지 경로 입력 (_IMAG01_1.jpg 형태)")

            if jpg_base_url:
                # 첫 컷 표시
                first_cut_url = jpg_base_url
                response = requests.get(first_cut_url)
                if response.status_code == 200:
                    st.image(Image.open(BytesIO(response.content)), caption="첫 컷 미리보기")

                if st.button("에피소드 등록 및 첫 컷 저장"):
                    new_ep = Episode(
                        webtoon_id=selected_webtoon.id,
                        episode_number=1,
                        lang='kr',
                        url=episode_url,
                        jpg_url=jpg_base_url
                    )
                    session.add(new_ep)
                    session.commit()

                    # 첫 컷 저장
                    image = Image.open(BytesIO(response.content))
                    image_height = image.height

                    cut_image = CutImage(
                        webtoon_id=selected_webtoon.id,
                        episode_id=new_ep.id,
                        cut_number=1,
                        image_path=first_cut_url,  # 경로 대신 URL 저장
                        height_px=image_height
                    )
                    session.add(cut_image)
                    session.commit()

                    st.success("✅ 첫 컷 저장 완료!")
                    episode = new_ep

        # 4. 컷 이미지 다음 버튼으로 뷰어
        if episode:
            st.markdown("---")
            st.subheader("📖 컷 이미지 뷰어")

            cut_images = session.query(CutImage).filter_by(
                episode_id=episode.id
            ).order_by(CutImage.cut_number).all()

            index = st.number_input("컷 번호", min_value=1, max_value=len(cut_images)+1, value=1, step=1)

            if index <= len(cut_images):
                cut = cut_images[index - 1]
                if os.path.exists(cut.image_path):
                    st.image(Image.open(cut.image_path), caption=f"컷 {index}", use_column_width=True)
                else:
                    st.error("이미지 파일을 찾을 수 없습니다.")
            else:
                if st.button("📥 다음 컷 가져오기"):
                    next_index = len(cut_images) + 1
                    base_url = episode.jpg_url.rsplit('_', 1)[0]
                    next_url = f"{base_url}_{next_index}.jpg"
                    res = requests.get(next_url)

                    if res.status_code == 200:
                        path = f"images/episode_{episode.id}_{next_index}.jpg"
                        with open(path, 'wb') as f:
                            f.write(res.content)

                        img = Image.open(BytesIO(res.content))
                        height = img.height

                        new_cut = CutImage(
                            webtoon_id=selected_webtoon.id,
                            episode_id=episode.id,
                            cut_number=next_index,
                            image_path=path,
                            height_px=height
                        )
                        session.add(new_cut)
                        session.commit()

                        st.success("✅ 컷 저장 완료!")
                        st.image(img, caption=f"컷 {next_index}", use_column_width=True)
                    else:
                        st.warning("더 이상 이미지를 불러올 수 없습니다.")

    session.close()
