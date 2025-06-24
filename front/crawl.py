import streamlit as st
from function.crawler import capture_webtoon_image
from PIL import Image
import os

def show():
    st.header("🕸 웹툰 크롤링 + OCR 분석")
    url = st.text_input("웹툰 URL을 입력하세요", placeholder="https://webtoon.example.com/episode/123")

    if st.button("크롤링 및 이미지 저장"):
        if url:
            st.info("🔄 웹툰 페이지를 크롤링 중입니다...")
            image_paths = capture_webtoon_image(url)

            if image_paths:
                st.success("✅ 이미지 캡처 완료!")
                st.write("👇 아래에서 이미지 파일을 다운로드할 수 있습니다.")

                for path in image_paths:
                    if os.path.exists(path):
                        with open(path, "rb") as file:
                            btn_label = f"💾 {os.path.basename(path)} 다운로드"
                            st.download_button(
                                label=btn_label,
                                data=file,
                                file_name=os.path.basename(path),
                                mime="image/png"
                            )
            else:
                st.error("이미지 캡처에 실패했습니다.")
        else:
            st.warning("URL을 입력해주세요.")