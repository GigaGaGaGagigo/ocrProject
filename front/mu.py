import streamlit as st
from function.crawler import capture_webtoon_image
from function.ocr import extract_text_from_image
from PIL import Image
import os

def show():
    
    st.title("📄 컨테이너로 나눈 페이지 예시")

    # ✅ 상단 버튼 (뒤로가기, 의견 추가)
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])

        with col1:
            if st.button("← 뒤로가기"):
                st.write("뒤로가기 실행")

        with col3:
            if st.button("의견추가"):
                st.write("의견 추가하기")

    # ✅ 본문 이미지 비교 영역
    with st.container():
        st.subheader("🔸 링크를 넣어주세요")

        undo_col1, img_col1, img_col2, next_col1 = st.columns(4)

        with undo_col1:
            if st.button("↩️ 되돌리기"):
                st.write("되돌리기 클릭됨")
            st.markdown("""
                <style>
                .custom-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px 40px;
                    font-size: 20px;
                    border: none;
                    border-radius: 10px;
                }
                </style>
                <button class="custom-button">🔙</button>
            """, unsafe_allow_html=True)

        with img_col1:
            st.image("image/image.png", caption="이미지1", use_column_width=True)

        with img_col2:
            st.image("image/image.png", caption="이미지2", use_column_width=True)

        with next_col1:
            if st.button("➡️ 다음"):
                st.write("다음 클릭됨")
            st.markdown("""
                <style>
                .custom-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px 40px;
                    font-size: 20px;
                    border: none;
                    border-radius: 10px;
                }
                </style>
                <button class="custom-button">🔜</button>
            """, unsafe_allow_html=True)

    # ✅ 하단 선택 영역
    with st.container():
        st.markdown("---")
        st.subheader("틀린그림찾기:")
        selected = st.radio("정답을 선택하세요:", ["다른게 있다", "다른게 없다", "모르겠다"])
        st.write(f"선택된 옵션: {selected}")

    # ✅ 페이지 이동
    with st.container():
        st.page_link("main2.py", label="➡ 다음 페이지", icon="➡")
        if st.button("다음으로"):
            st.success("다음 단계로 이동합니다.")