import streamlit as st
from PIL import Image
import requests
import numpy as np
import easyocr
from io import BytesIO

# EasyOCR 리더 초기화 (한글 + 영어)
reader = easyocr.Reader(['ko', 'en'])

# Streamlit 설정
st.set_page_config(page_title="웹툰 이미지 URL OCR", layout="centered")

st.title("🌐 웹툰 이미지 URL 텍스트 추출기")
st.write("이미지 URL을 입력하면 웹툰 컷 속 텍스트를 추출합니다.")
st.markdown("---")

# 이미지 URL 입력 받기
image_url = st.text_input("이미지 URL을 입력하세요", placeholder="https://...IMAG01_1.jpg")

if image_url:
    headers = {
    "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(image_url, headers=headers, timeout=5)
        if response.status_code == 200 and 'image' in response.headers.get("Content-Type", ""):
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="불러온 이미지", use_column_width=True)

            with st.spinner("🔍 텍스트 인식 중..."):
                result = reader.readtext(np.array(image), detail=0)

            st.markdown("### 📋 추출된 텍스트")
            if result:
                for i, line in enumerate(result, 1):
                    st.write(f"**{i}.** {line}")
            else:
                st.warning("텍스트를 인식하지 못했습니다. 다른 이미지를 시도해 보세요.")
        else:
            st.error(f"이미지를 불러오는 데 실패했습니다. 상태 코드: {response.status_code}")
    except Exception as e:
        st.error(f"이미지 로드 중 오류 발생: {e}")
else:
    st.info("📎 이미지 URL을 입력하면 텍스트를 자동 추출합니다.")

st.markdown("---")
st.caption("🧠 Made with EasyOCR + Streamlit")
