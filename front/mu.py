import streamlit as st
from function.crawler import capture_webtoon_image
from function.ocr import extract_text_from_image
from PIL import Image
import os


def show():
    
    st.title("📄 컨테이너로 나눈 페이지 예시")

# 컨테이너 1: 헤더 영역
with st.container():
    col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    if st.button("← 뒤로가기"):
        st.write("뒤로가기 실행")

with col3:
    if st.button("의견추가"):
        st.write("의견 추가하기")
    #st.header("🔹 상단 영역")
    #st.write("웹툰을 넣어주세요.")

# 컨테이너 2: 본문 영역
with st.container():
    st.subheader("🔸 링크를 넣어주세요")
    undo_col1, col1, col2, next_col1 = st.columns(4)  # 4개의 열 생성
with undo_col1:()

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
with col1:
        st.image("image/image.png", caption="이미지 1")
with col2:
        st.image("image/image.png", caption="이미지 2")
with next_col1:
    #st.button("➡️ 다음")
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

# 컨테이너 3: 하단 선택지
with st.container():
    st.subheader("🔻 하단 선택 영역")
    option = st.radio("선택하세요:", ["A", "B", "C"])
    st.write(f"선택한 항목: {option}")

# 컨테이너 4: 하단 버튼
with st.container():
    if st.button("다음으로"):
        st.success("다음 단계로 이동합니다.")
