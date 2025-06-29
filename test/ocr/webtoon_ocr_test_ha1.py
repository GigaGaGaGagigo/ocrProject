import streamlit as st
from PIL import Image
import easyocr
import numpy as np
import cv2

# EasyOCR 리더 초기화
reader = easyocr.Reader(['ko', 'en'])

st.set_page_config(page_title="웹툰 말풍선 OCR", layout="wide")
st.title("📖 웹툰 말풍선 인식기")
st.write("말풍선을 감지하고, 각 영역에서 텍스트를 추출합니다.")
st.markdown("---")

# 말풍선 감지 및 OCR 함수
def detect_speech_bubbles_and_ocr(pil_image):
    image = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # 밝은 영역(말풍선) 탐지용 threshold
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)

    # 외곽선 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated_img = image.copy()
    all_texts = []
    bubble_crops = []  # 크롭된 말풍선 이미지를 저장할 리스트

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 30:  # 너무 작은 말풍선은 무시
            bubble_crop = image[y:y + h, x:x + w]
            bubble_crops.append(bubble_crop)  # 크롭 이미지 리스트에 추가
            text = reader.readtext(bubble_crop, detail=0)
            all_texts.append({
                "text": text,
                "crop": bubble_crop
            })
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    return annotated_img, all_texts, bubble_crops  # 크롭 이미지도 반환

# 업로드 UI
uploaded_file = st.file_uploader("웹툰 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 원본 이미지", use_column_width=True)

    with st.spinner("말풍선 감지 중..."):
        annotated, texts, bubble_crops = detect_speech_bubbles_and_ocr(image)  # 크롭 이미지도 받음

    st.markdown("### 📍 감지된 말풍선 (박스 표시)")
    st.image(annotated, channels="RGB", use_column_width=True)

    st.markdown("### 🖼️ 감지된 말풍선 개별 이미지")
    if bubble_crops:
        # 크롭된 이미지를 한 줄에 4개씩 썸네일로 보여주기
        cols = st.columns(4)
        for i, crop in enumerate(bubble_crops):
            with cols[i % 4]:
                st.image(crop, caption=f"Bubble {i+1}", use_column_width=True)
    else:
        st.info("감지된 말풍선 이미지가 없습니다.")

    st.markdown("### 📋 추출된 텍스트")
    if texts:
        for i, t in enumerate(texts, 1):
            st.write(f"**{i}.** {' / '.join(t['text']) if isinstance(t['text'], list) else t['text']}")
    else:
        st.warning("말풍선 텍스트가 인식되지 않았습니다. 이미지 품질 또는 말풍선 색상을 확인하세요.")
else:
    st.info("이미지를 업로드하면 감지 및 텍스트 추출이 시작됩니다.")

st.markdown("---")
st.caption("말풍선 감지 기반 OCR v1.0 (EasyOCR + OpenCV)")