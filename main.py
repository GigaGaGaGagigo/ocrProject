import streamlit as st
from front import home, crawl

st.set_page_config(page_title="웹툰 OCR 학습기", layout="centered")

st.title("📘 웹툰 기반 AI 언어 학습")
page = st.sidebar.selectbox("📌 페이지 선택", ["홈", "크롤링"])

if page == "홈":
    home.show()
elif page == "크롤링":
    crawl.show()