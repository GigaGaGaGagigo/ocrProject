import sys
import os
# 📌 function 폴더 접근 위해 루트 경로로 이동
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
import cv2
from PIL import Image   
from function.ocr_paddle import paddleocr_analyze


# 🔧 시각화 함수
def draw_boxes(image, boxes, color=(255, 0, 0)):
    for box in boxes:
        x, y, w, h = box[:4]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
    return image


# 🚀 PaddleOCR Streamlit 페이지
def show():
    st.title("🟦 PaddleOCR 테스트 페이지")
    uploaded = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

    if uploaded:
        img_path = "temp_test_paddleocr.jpg"

        try:
            # 이미지 저장
            with open(img_path, "wb") as f:
                f.write(uploaded.read())

            st.subheader("📸 업로드된 이미지")
            st.image(uploaded, use_container_width=True)

            # PaddleOCR 분석 실행
            paddle_merged = paddleocr_analyze(img_path)

            # 🗨️ 말풍선 단위 병합 결과 출력
            st.markdown("**🗨️ 말풍선 단위 병합 결과:**")
            for i, (x, y, w, h, text, conf) in enumerate(paddle_merged):
                st.write(f"{i+1:02d}. \"{text}\" (신뢰도 평균: {conf:.2f})")

            # 시각화
            image = cv2.imread(img_path)
            image = draw_boxes(image, paddle_merged, color=(255, 0, 0))
            st.image(image, channels="BGR", caption="🟦 PaddleOCR - 병합 시각화", use_container_width=True)

        finally:
            # 🔥 임시 이미지 삭제
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"[삭제 완료] {img_path}")


if __name__ == "__main__":
    show()