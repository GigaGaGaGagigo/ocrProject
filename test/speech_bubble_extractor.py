import streamlit as st
import cv2
import numpy as np
import os
from PIL import Image

def extract_speech_bubbles_improved(image, save_debug=False):
    """개선된 말풍선 검출 함수 (numpy array 입력)"""
    
    if image is None:
        st.error("이미지를 읽을 수 없습니다")
        return [], None
    
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 1. 전처리: 흰색 영역 강조
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 2. 모폴로지 연산으로 노이즈 제거 및 연결
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # 3. 윤곽선 검출
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    debug_image = original.copy() if save_debug else None
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # 말풍선 크기 필터링
        if 5000 < area < (image.shape[0] * image.shape[1] * 0.3):
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            x, y, w, h = cv2.boundingRect(contour)
            
            aspect_ratio = w / float(h)
            if 0.3 < aspect_ratio < 3.0:
                bubble = original[y:y+h, x:x+w]
                bubbles.append({
                    'image': bubble,
                    'bbox': (x, y, w, h),
                    'area': area,
                    'contour': contour
                })
                
                if save_debug and debug_image is not None:
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(debug_image, f"Bubble {len(bubbles)}", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return bubbles, debug_image

def main():
    st.set_page_config(page_title="웹툰 말풍선 추출기", layout="wide")
    
    st.title("🗨️ 웹툰 말풍선 추출기")
    st.markdown("웹툰 이미지에서 말풍선을 자동으로 검출합니다.")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # Threshold 조절
        threshold_value = st.slider("이진화 임계값", 150, 250, 200, step=5)
        
        # 최소/최대 면적 설정
        min_area = st.slider("최소 말풍선 크기", 1000, 10000, 5000, step=500)
        max_area_ratio = st.slider("최대 말풍선 크기 비율", 0.1, 0.5, 0.3, step=0.05)
        
        # 가로세로 비율 설정
        min_aspect = st.slider("최소 가로세로 비율", 0.1, 1.0, 0.3, step=0.1)
        max_aspect = st.slider("최대 가로세로 비율", 1.0, 5.0, 3.0, step=0.5)
        
        show_debug = st.checkbox("디버그 이미지 표시", value=True)
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "웹툰 이미지를 업로드하세요", 
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="JPG, JPEG, PNG, BMP 형식을 지원합니다."
    )
    
    if uploaded_file is not None:
        # 이미지 읽기
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # 원본 이미지 표시
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 원본 이미지")
            # OpenCV BGR을 RGB로 변환
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            st.image(image_rgb, use_column_width=True)
        
        # 말풍선 추출 (수정된 파라미터 적용)
        def extract_with_params(image):
            original = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            
            kernel = np.ones((3,3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            bubbles = []
            debug_image = original.copy()
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if min_area < area < (image.shape[0] * image.shape[1] * max_area_ratio):
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / float(h)
                    
                    if min_aspect < aspect_ratio < max_aspect:
                        bubble = original[y:y+h, x:x+w]
                        bubbles.append({
                            'image': bubble,
                            'bbox': (x, y, w, h),
                            'area': area
                        })
                        
                        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        cv2.putText(debug_image, f"{len(bubbles)}", 
                                   (x+5, y+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            return bubbles, debug_image
        
        # 추출 실행
        with st.spinner('말풍선을 검출하는 중...'):
            bubbles, debug_image = extract_with_params(image)
        
        with col2:
            if show_debug and debug_image is not None:
                st.subheader("🔍 검출 결과")
                debug_rgb = cv2.cvtColor(debug_image, cv2.COLOR_BGR2RGB)
                st.image(debug_rgb, use_column_width=True)
        
        # 검출 결과 표시
        st.markdown("---")
        st.subheader(f"📊 검출된 말풍선: {len(bubbles)}개")
        
        if bubbles:
            # 말풍선 그리드 표시
            cols_per_row = 4
            for i in range(0, len(bubbles), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(bubbles):
                        with cols[j]:
                            bubble_info = bubbles[i + j]
                            bubble_img = bubble_info['image']
                            x, y, w, h = bubble_info['bbox']
                            
                            # BGR을 RGB로 변환
                            bubble_rgb = cv2.cvtColor(bubble_img, cv2.COLOR_BGR2RGB)
                            
                            st.image(bubble_rgb, use_column_width=True,
                                   caption=f"말풍선 #{i+j+1}\n위치: ({x}, {y})\n크기: {w}×{h}")
                            
                            # 다운로드 버튼
                            # OpenCV 이미지를 PIL Image로 변환
                            pil_image = Image.fromarray(bubble_rgb)
                            
                            # PIL Image를 bytes로 변환
                            import io
                            buf = io.BytesIO()
                            pil_image.save(buf, format='PNG')
                            byte_im = buf.getvalue()
                            
                            st.download_button(
                                label=f"💾 #{i+j+1} 저장",
                                data=byte_im,
                                file_name=f"bubble_{i+j+1}.png",
                                mime="image/png"
                            )
        else:
            st.info("검출된 말풍선이 없습니다. 설정을 조정해보세요.")
        
        # 전체 결과 다운로드
        if bubbles and st.button("📥 모든 말풍선 ZIP으로 다운로드"):
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, bubble_info in enumerate(bubbles):
                    bubble_img = bubble_info['image']
                    bubble_rgb = cv2.cvtColor(bubble_img, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(bubble_rgb)
                    
                    img_buffer = io.BytesIO()
                    pil_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    zip_file.writestr(f"bubble_{i+1}.png", img_buffer.getvalue())
            
            zip_buffer.seek(0)
            st.download_button(
                label="💾 ZIP 파일 다운로드",
                data=zip_buffer.getvalue(),
                file_name="speech_bubbles.zip",
                mime="application/zip"
            )
    
    else:
        # 사용 가이드
        st.info("👆 웹툰 이미지를 업로드하면 자동으로 말풍선을 검출합니다.")
        
        with st.expander("📖 사용 방법"):
            st.markdown("""
            1. **이미지 업로드**: 웹툰 이미지를 드래그 앤 드롭하거나 파일 선택
            2. **파라미터 조정**: 왼쪽 사이드바에서 검출 설정 조정
            3. **결과 확인**: 검출된 말풍선 확인 및 개별 다운로드
            4. **일괄 다운로드**: 모든 말풍선을 ZIP 파일로 다운로드
            
            **💡 팁:**
            - 말풍선이 잘 검출되지 않으면 임계값을 조정해보세요
            - 너무 많은 영역이 검출되면 최소 크기를 늘려보세요
            - 말풍선 모양에 따라 가로세로 비율을 조정하세요
            """)

if __name__ == "__main__":
    main()