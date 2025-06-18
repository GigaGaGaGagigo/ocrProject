import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# EasyOCR 리더 초기화 (한글 + 영어 지원)
reader = easyocr.Reader(['ko', 'en'])

# Streamlit UI 구성
st.set_page_config(page_title="웹툰 이미지 텍스트 추출기", layout="centered")

st.title("📖 웹툰 이미지 텍스트 추출기 (EasyOCR)")
st.write("웹툰 이미지 속 말풍선 텍스트를 인식해 추출합니다.")
st.markdown("---")

uploaded_file = st.file_uploader("웹툰 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 이미지", use_column_width=True)

    with st.spinner("텍스트 추출 중..."):
        result = reader.readtext(np.array(image), detail=0)

    st.markdown("### 📋 추출된 텍스트")
    for i, line in enumerate(result, 1):
        st.write(f"**{i}.** {line}")

    if not result:
        st.warning("텍스트가 인식되지 않았습니다. 이미지 품질을 확인해 주세요.")
else:
    st.info("왼쪽 사이드바 또는 위에서 이미지를 업로드하세요.")

st.markdown("---")
st.caption("Made with ❤️ using EasyOCR & Streamlit")