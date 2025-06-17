from PIL import Image
import pytesseract
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="웹툰 글자 인식 학습기", layout="centered")

# 제목과 설명
st.title("📚 웹툰 글자 인식 학습기")
st.markdown("""
웹툰 이미지에서 **말풍선 속 글자나 자막**을 추출하는 도구입니다.  
OCR 결과는 **교육용**이나 **제작 보조** 용도로 활용할 수 있습니다.
""")

# 이미지 업로드
uploaded_file = st.file_uploader("웹툰 이미지 업로드", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 웹툰 이미지", use_column_width=True)

    with st.spinner("텍스트 추출 중..."):
        # OCR 실행 (한글 + 영어)
        result = pytesseract.image_to_string(image, lang="kor+eng")

    # 결과 출력
    st.subheader("📝 인식된 대사 / 텍스트")
    st.text_area(label="", value=result, height=300)
else:
    st.info("왼쪽 사이드바 또는 위에서 웹툰 이미지를 업로드해주세요.")