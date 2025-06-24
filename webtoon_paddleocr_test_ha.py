import streamlit as st
from PIL import Image
import numpy as np
import cv2
from paddleocr import PaddleOCR
import os

# PaddleOCR 리더 초기화 ('korean'만으로 한/영 모두 인식 시도)
ocr = PaddleOCR(lang='korean', use_angle_cls=True)

st.set_page_config(page_title="웹툰 말풍선 OCR", layout="wide")
st.title("📖 웹툰 말풍선 인식기 (PaddleOCR)")
st.write("말풍선을 감지하고, 각 영역에서 텍스트를 추출합니다.")
st.markdown("---")

# crop 디버그 폴더(선택)
CROP_DEBUG_DIR = "crop_debug"
if not os.path.exists(CROP_DEBUG_DIR):
    os.makedirs(CROP_DEBUG_DIR)

# 말풍선 감지 및 OCR 함수
def detect_speech_bubbles_and_ocr_paddle(pil_image):
    image = np.array(pil_image.convert("RGB"))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # threshold 조정/실험: 160~220 (or adaptive)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    # adaptive threshold로 바꿔보고 싶으면 아래 주석 해제
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated_img = image.copy()
    all_texts = []
    bubble_crops = []

    for idx, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 30:
            bubble_crop = image[y:y + h, x:x + w]
            bubble_crops.append(bubble_crop)
            # 디버깅용 crop 이미지 저장(선택)
            # cv2.imwrite(os.path.join(CROP_DEBUG_DIR, f"crop_{idx}_{x}_{y}.png"), bubble_crop)

            # PaddleOCR 적용 - ndarray 또는 파일 경로 모두 사용 가능
            result = ocr.ocr(bubble_crop)
            texts = []
            # PaddleOCR 결과 robust하게 파싱
            if result and isinstance(result, list):
                for line in result:
                    # [ [box], (text, conf) ] 구조
                    if isinstance(line, list) and len(line) > 1 and isinstance(line[1], tuple):
                        text = line[1][0]
                        # 공백 등 불필요한 텍스트는 제거
                        if text.strip():
                            texts.append(text)
            all_texts.append({
                "text": texts,
                "crop": bubble_crop
            })
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    return annotated_img, all_texts, bubble_crops

# 업로드 UI
uploaded_file = st.file_uploader("웹툰 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 원본 이미지", use_container_width=True)

    with st.spinner("말풍선 감지 중..."):
        annotated, texts, bubble_crops = detect_speech_bubbles_and_ocr_paddle(image)

    st.markdown("### 📍 감지된 말풍선 (박스 표시)")
    st.image(annotated, channels="RGB", use_container_width=True)

    st.markdown("### 🖼️ 감지된 말풍선 개별 이미지")
    if bubble_crops:
        cols = st.columns(4)
        for i, crop in enumerate(bubble_crops):
            with cols[i % 4]:
                st.image(crop, caption=f"Bubble {i+1}", use_container_width=True)
    else:
        st.info("감지된 말풍선 이미지가 없습니다.")

    st.markdown("### 📋 추출된 텍스트")
    if texts:
        for i, t in enumerate(texts, 1):
            # 여러 줄이 추출될 수 있음
            text_result = ' / '.join(t['text']) if isinstance(t['text'], list) else t['text']
            st.write(f"**{i}.** {text_result if text_result else '(텍스트 없음)'}")
    else:
        st.warning("말풍선 텍스트가 인식되지 않았습니다. 이미지 품질 또는 말풍선 색상을 확인하세요.")
else:
    st.info("이미지를 업로드하면 감지 및 텍스트 추출이 시작됩니다.")

st.markdown("---")
st.caption("말풍선 감지 기반 OCR v1.0 (PaddleOCR + OpenCV)")