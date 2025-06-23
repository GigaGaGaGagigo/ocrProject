import streamlit as st
from function.crawler import capture_webtoon_image
from function.ocr import extract_text_from_image
from PIL import Image
import os

def show():
    st.header("🕸 웹툰 크롤링 + OCR 분석")
    url = st.text_input("웹툰 URL을 입력하세요", placeholder="https://webtoon.example.com/episode/123")

    if st.button("크롤링 및 텍스트 추출"):
        if url:
            st.info("🔄 웹툰 페이지를 크롤링 중입니다...")
            image_path = capture_webtoon_image(url)

            if os.path.exists(image_path):
                st.success("✅ 이미지 캡처 완료!")
                st.image(Image.open(image_path), caption="캡처된 웹툰 이미지", use_column_width=True)

                st.info("🧠 OCR 인식 중...")
                text_result = extract_text_from_image(image_path)
                st.subheader("📋 인식된 텍스트")
                st.text(text_result)
            else:
                st.error("이미지 캡처에 실패했습니다.")
        else:
            st.warning("URL을 입력해주세요.")