import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from db.database import SessionLocal
from db.crawl_sql import Webtoon, CutImage, Episode
from function.code_label import GENRE_MAP, GENRE_LABEL_TO_CODE
import time
import io
import os

st.set_page_config(page_title="웹툰 비교 뷰어", layout="wide")
st.title("📖 한영 웹툰 컷 비교 뷰어")

# 🧩 한글 URL에서 컷 번호 조합
def jpg_url_update(url: str, num: int) -> str:
    url = url[:-5]
    while url and url[-1] != '_':
        url = url[:-1]
    if url.endswith('_'):
        return f"{url}{num}.jpg"
    else:
        raise ValueError("유효한 base URL 형식이 아닙니다.")

# 🧩 영어 웹툰 캡처 함수 (시작 y에서 50px 아래서 자르기)
def capture_webtoon_crop(url, y_start, y_end, cute_size: int, target_height=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1600,6000')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(0.5)

    driver.execute_script(f"window.scrollTo(0, {y_start})")
    time.sleep(0.5)
    png = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(png))

    adjusted_start = cute_size  # 상단 50px 잘라냄
    adjusted_end = adjusted_start + (y_end - y_start)
    cropped = image.crop((440, adjusted_start, 1600 - 470, adjusted_end))  # 좌우 잘라냄

    # 📏 높이 맞추기 (한글 컷과 동일하게)
    if target_height:
        aspect_ratio = cropped.width / cropped.height
        target_width = int(aspect_ratio * target_height)
        cropped = cropped.resize((target_width, target_height), Image.BILINEAR)

    return cropped

def select_webtoon():
    session = SessionLocal()

    # 웹툰 보기 모드 상태 확인
    if st.session_state.get("view_mode") == "reader":
        selected_ep_kr = st.session_state["selected_ep_kr"]
        selected_ep_en = st.session_state.get("selected_ep_en")
        webtoon_read(selected_ep_kr, selected_ep_en)
        return  # 함수 종료하여 아래 UI 안 보이게 함

    # ✅ 본문 영역 상단에 검색 필터 표시
    st.subheader("🔍 웹툰 검색")
    col1, col2 = st.columns([1, 5])
    with col1:
        selected_genre = st.selectbox("장르 선택", ["전체"] + list(GENRE_MAP.values()))
    with col2:
        search_keyword = st.text_input("웹툰 제목 검색")

    # --- 웹툰 필터링 ---
    query = session.query(Webtoon).filter(Webtoon.language == 'kr')
    if selected_genre != "전체":
        genre_code = list(GENRE_MAP.keys())[list(GENRE_MAP.values()).index(selected_genre)]
        query = query.filter(Webtoon.genre == genre_code)
    if search_keyword:
        query = query.filter(Webtoon.title.contains(search_keyword))

    webtoon_list = query.order_by(Webtoon.title).all()

    if search_keyword and webtoon_list:
        st.subheader("🇰🇷 웹툰 목록")
        selected_webtoon = st.selectbox("웹툰 선택", webtoon_list, format_func=lambda w: w.title)

        if selected_webtoon:
            st.markdown(f"### ✏️ 선택한 웹툰: {selected_webtoon.title}")
            
            ep_kr = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="kr").order_by(Episode.episode_number).all()
            ep_en = session.query(Episode).filter_by(webtoon_id=selected_webtoon.id, lang="en").order_by(Episode.episode_number).all()

            kr_eps = [f"{ep.episode_number}화" for ep in ep_kr]
            selected_idx = st.selectbox("🇰🇷 에피소드 선택", list(range(1, len(kr_eps)+1)), format_func=lambda i: kr_eps[i-1])

            if selected_idx:
                selected_ep_kr = ep_kr[selected_idx - 1]
                selected_ep_en = ep_en[selected_idx - 1] if len(ep_en) >= selected_idx else None

                st.markdown("---")
                st.markdown(f"### 🇰🇷 한글 에피소드 정보")
                st.write(f"- 에피소드 번호: {selected_ep_kr.episode_number}")
                st.write(f"- URL: {selected_ep_kr.url}")
                st.write(f"- 이미지 경로: {selected_ep_kr.jpg_url}")
                st.write(f"- 컷 수: {selected_ep_kr.cut_size}")

                if selected_ep_en:
                    st.markdown(f"### 🇺🇸 영어 에피소드 정보")
                    st.write(f"- 에피소드 번호: {selected_ep_en.episode_number}")
                    st.write(f"- URL: {selected_ep_en.url}")
                else:
                    st.warning("❌ 해당 회차의 영어 버전이 존재하지 않습니다.")

                if st.button("📖 이 회차 보기"):
                    # 세션에 정보 저장하고 다음 호출 시 바로 보기 모드 진입
                    st.session_state["view_mode"] = "reader"
                    st.session_state["selected_ep_kr"] = selected_ep_kr
                    st.session_state["selected_ep_en"] = selected_ep_en
                    st.rerun()  # 화면 다시 그리기

    elif search_keyword:
        st.warning("❌ 해당 검색어에 맞는 웹툰이 없습니다.")



def webtoon_read(ep_kr: Episode, ep_en: Episode):

    session = SessionLocal()

    # 🧩 세션 상태 초기화
    for key, default in {
        "kr_url": "",
        "en_url": "",
        "cut_index": 1,
        "kor_heights": []
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ◀️ 이전 / 다음 ▶️ 버튼
    left, center, right = st.columns([1, 6, 1])
    with left:
        # 여백
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        if st.button("◀️ 이전 컷") and st.session_state.cut_index > 1:
            st.session_state.cut_index -= 1
    with right:
        # 여백
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        if st.button("다음 컷 ▶️"):
            st.session_state.cut_index += 1

    # 🔗 URL 입력
    with center:
        if not ep_kr.jpg_url or not ep_en.url:
            st.warning("한글/영어 URL이 모두 필요합니다.")
            st.stop()

        st.session_state.kr_url = ep_kr.jpg_url
        st.session_state.en_url = ep_en.url

        idx = st.session_state.cut_index
        headers = {"User-Agent": "Mozilla/5.0"}
        st.markdown(f"### 🖼 컷 번호: {idx}")

        # 여기 코드 추가
        # 🔍 CutImage 검색 및 렌더링
        kr_cut = session.query(CutImage).filter_by(
            episode_id=ep_kr.id,
            cut_number=idx
        ).first()

        en_cut = session.query(CutImage).filter_by(
            episode_id=ep_en.id,
            cut_number=idx
        ).first()

        col_kr, col_en = st.columns(2)

        if(kr_cut and en_cut):
            with col_kr:
                try:
                    response = requests.get(kr_cut.image_path, headers=headers)
                    if response.status_code == 200:
                        kr_img = Image.open(BytesIO(response.content))
                        st.image(kr_img, use_container_width=True)

                    else:
                        st.warning("❌ 한글 컷을 불러올 수 없습니다.")
                except Exception as e:
                    st.error(f"한글 URL 오류: {e}")

            # 🇺🇸 영어 컷 (같은 높이 만큼만 잘라서 표시)
            with col_en:    
                try:

                    filename = "image/" + en_cut.image_path
                    st.image(filename)
                    
                except Exception as e:
                    st.warning(f"영어 웹툰 캡처 실패: {e}")
        else:
            # 🇰🇷 한글 컷
            kr_img_height = None
            with col_kr:
                try:
                    kr_full_url = jpg_url_update(st.session_state.kr_url, idx)
                    response = requests.get(kr_full_url, headers=headers)
                    if response.status_code == 200:
                        kr_img = Image.open(BytesIO(response.content))
                        kr_img_height = kr_img.height
                        st.image(kr_img, use_container_width=True)

                        # 컷별 높이 기록
                        if len(st.session_state.kor_heights) < idx:
                            accumulated = sum(h[1] - h[0] for h in st.session_state.kor_heights)
                            st.session_state.kor_heights.append((accumulated, accumulated + kr_img_height))
                        
                        if(kr_cut is None):
                            # db에 저장
                            new_kr_cut = CutImage(
                                episode_id=ep_kr.id,
                                cut_number=idx,
                                image_path=kr_full_url,
                                height_px=kr_img_height
                            )
                            session.add(new_kr_cut)
                            session.commit()

                    else:
                        st.warning("❌ 한글 컷을 불러올 수 없습니다.")
                except Exception as e:
                    st.error(f"한글 URL 오류: {e}")

            # 🇺🇸 영어 컷 (같은 높이 만큼만 잘라서 표시)
            with col_en:
                try:
                    
                    y_start, y_end = st.session_state.kor_heights[idx - 1]
                    eng_crop = capture_webtoon_crop(
                        st.session_state.en_url,
                        y_start,
                        y_end,
                        ep_en.cut_size,
                        target_height=kr_img_height if kr_img_height else None   # 높이 맞추기
                    )

                    # 이미지 보여주기
                    st.image(eng_crop, use_container_width=True)

                    # --- 이미지 저장 ---
                    save_dir = "image"
                    os.makedirs(save_dir, exist_ok=True)
                    filename = f"{ep_en.webtoon_id}_{ep_en.episode_number}_{idx}.jpg"
                    save_path = os.path.join(save_dir, filename)

                    # 저장
                    eng_crop.save(save_path, format="JPEG", quality=90)

                    # db에 저장
                    new_en_cut = CutImage(
                        episode_id=ep_en.id,
                        cut_number=idx,
                        image_path=filename,
                        height_px=kr_img_height
                    )
                    session.add(new_en_cut)
                    session.commit()

                except Exception as e:
                    st.warning(f"영어 웹툰 캡처 실패: {e}")

    session.close()