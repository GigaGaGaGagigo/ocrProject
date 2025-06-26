import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import io

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
def capture_webtoon_crop(url, y_start, y_end, target_height=None):
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

    adjusted_start = 50  # 상단 50px 잘라냄
    adjusted_end = adjusted_start + (y_end - y_start)
    cropped = image.crop((440, adjusted_start, 1600 - 470, adjusted_end))  # 좌우 잘라냄

    # 📏 높이 맞추기 (한글 컷과 동일하게)
    if target_height:
        aspect_ratio = cropped.width / cropped.height
        target_width = int(aspect_ratio * target_height)
        cropped = cropped.resize((target_width, target_height), Image.BILINEAR)

    return cropped

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
    if st.button("◀️ 이전 컷") and st.session_state.cut_index > 1:
        st.session_state.cut_index -= 1
with right:
    if st.button("다음 컷 ▶️"):
        st.session_state.cut_index += 1

# 🔗 URL 입력
with center:
    st.write("**🌐 이미지 URL 입력**")
    kr_url_input = st.text_input("🇰🇷 한글 컷 URL (예: https://...IMAG01_1.jpg)", value=st.session_state.kr_url)
    en_url_input = st.text_input("🇺🇸 영어 웹툰 웹페이지 URL", value=st.session_state.en_url)

    if kr_url_input:
        st.session_state.kr_url = kr_url_input
    if en_url_input:
        st.session_state.en_url = en_url_input

    idx = st.session_state.cut_index
    headers = {"User-Agent": "Mozilla/5.0"}
    st.markdown(f"### 🖼 컷 번호: {idx}")
    col_kr, col_en = st.columns(2)

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
            else:
                st.warning("❌ 한글 컷을 불러올 수 없습니다.")
        except Exception as e:
            st.error(f"한글 URL 오류: {e}")

    # 🇺🇸 영어 컷 (같은 높이 만큼만 잘라서 표시)
    with col_en:
        try:
            if len(st.session_state.kor_heights) >= idx:
                y_start, y_end = st.session_state.kor_heights[idx - 1]
                eng_crop = capture_webtoon_crop(
                    st.session_state.en_url,
                    y_start,
                    y_end,
                    target_height=kr_img_height if kr_img_height else None  # 높이 맞추기
                )
                st.image(eng_crop, use_container_width=True)
            else:
                st.info("먼저 한글 컷을 불러오면 영어 캡처도 함께 출력됩니다.")
        except Exception as e:
            st.warning(f"영어 웹툰 캡처 실패: {e}")