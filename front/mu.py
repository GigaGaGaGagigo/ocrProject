import streamlit as st
from function.crawler import capture_webtoon_image
from function.ocr import extract_text_from_image
from PIL import Image
import os

def show():
    
    st.title("📄 무협")

    
    # ✅ 본문 이미지 비교 영역
    with st.container():
        st.subheader("🔸 영어링크를 넣어주세요")
        link_input = st.text_input("영어웹툰 링크", placeholder="https://example.com/webtoon..."
                                   ,key="ENwebtoon_link_input")

        if link_input:
            st.info(f"입력된 링크: {link_input}")
            # 필요 시 link_input을 기반으로 OCR 또는 이미지 처리 가능
        # ✅ 링크 입력 영역
    with st.container():
        st.subheader("🔸 한글 링크를 입력해주세요")
        link_input = st.text_input("웹툰 링크", placeholder="https://example.com/webtoon..."
                                   ,key="webtoon_link_input")

        if link_input:
            st.info(f"입력된 링크: {link_input}")
            # 필요 시 link_input을 기반으로 OCR 또는 이미지 처리 가능

        undo_col1, img_col1, img_col2, next_col1 = st.columns([0.2, 1.5, 1.5, 0.1])

        with undo_col1:
            if st.button("↩️ "):
                st.write("되돌리기 클릭됨")
          

        with img_col1:
            st.image("20250519192639_3b58aab64215b9c094c0e205a404a6a7_IMAG01_2.jpg", caption="영어", use_column_width=True)

        with img_col2:
            st.image("20250519192639_3b58aab64215b9c094c0e205a404a6a7_IMAG01_2.jpg", caption="한글", use_column_width=True)

        with next_col1:
            if st.button("➡️"):
                st.write("다음 클릭됨")
        
    # ✅ 하단 선택 영역
    with st.container():
        st.markdown("---")
        st.subheader("다음중 웹툰 속 대사로 나오지 않은 단어는?")
        selected = st.radio("정답을 선택하세요:", ["HI", "HELLO", "BYE"])
        st.write(f"선택된 옵션: {selected}")