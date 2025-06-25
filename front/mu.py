import streamlit as st
from function.crawler import capture_webtoon_image
from function.ocr import extract_text_from_image
from PIL import Image
import os

def show():
    
    st.title("📄 무협")

    
    # ✅ 본문 이미지 비교 영역
    with st.container():
        st.subheader("🔸 링크를 넣어주세요"), st.subheader("링크를 넣어주세요")

        undo_col1, img_col1, img_col2, next_col1 = st.columns([0.1, 1, 1, 0.1])

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
        st.subheader("퀴즈:")
        selected = st.radio("정답을 선택하세요:", ["다른게 있다", "다른게 없다", "모르겠다"])
        st.write(f"선택된 옵션: {selected}")

    # ✅ 페이지 이동
    with st.container():
        st.page_link("main2.py", label="➡ 다음 페이지", icon="➡")
        if st.button("다음으로"):
            st.success("다음 단계로 이동합니다.")