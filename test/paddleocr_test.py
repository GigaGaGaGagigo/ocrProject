from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import time

def visualize_paddleocr_results(img_path, use_angle_cls=True, use_space_char=True):
    """PaddleOCR 결과 시각화 (간단한 설정)"""
    print("PaddleOCR 디바이스: CPU")
    
    # PaddleOCR 초기화 (간단한 설정으로 에러 방지)
    print("PaddleOCR 모델 로딩 중...")
    try:
        ocr = PaddleOCR(
            lang="korean",
            use_gpu=False,  # Mac에서는 CUDA 미지원
            show_log=False,  # 로그 출력 줄이기
            use_angle_cls=use_angle_cls,  # 회전된 텍스트 인식
            use_space_char=use_space_char  # 공백 문자 인식
        )
    except Exception as e:
        print(f"PaddleOCR 초기화 오류: {e}")
        print("기본 설정으로 재시도...")
        ocr = PaddleOCR(lang="korean", use_gpu=False, show_log=False)
    
    # 이미지 읽기
    pil_img = Image.open(img_path)
    img = np.array(pil_img)
    
    # OCR 수행
    print("PaddleOCR 텍스트 인식 중...")
    start_time = time.time()
    result = ocr.ocr(img_path, cls=use_angle_cls)
    ocr_time = time.time() - start_time
    
    print(f"OCR 처리 시간: {ocr_time:.2f}초")
    
    # 결과 확인
    if result[0] is None:
        print("PaddleOCR: 텍스트를 찾을 수 없습니다.")
        return pil_img, [], [], ocr_time
    
    print(f"감지된 텍스트: {len(result[0])}개")
    
    # 결과 추출
    boxes = [line[0] for line in result[0]]
    txts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]
    
    # 시각화 (draw_ocr 사용)
    try:
        # Mac 시스템 폰트 경로들 시도
        font_paths = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break
        
        result_np = draw_ocr(img, boxes, txts, scores, font_path=font_path)
        result_img = Image.fromarray(result_np)
        
    except Exception as e:
        print(f"draw_ocr 오류: {e}")
        print("수동 시각화로 대체...")
        
        # 수동으로 박스 그리기
        result_img = pil_img.copy()
        draw = ImageDraw.Draw(result_img)
        
        # 폰트 설정
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # 박스와 텍스트 그리기
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        for i, (box, txt, score) in enumerate(zip(boxes, txts, scores)):
            color = colors[i % len(colors)]
            box = np.array(box).astype(np.int32)
            box_coords = [(box[0][0], box[0][1]), (box[1][0], box[1][1]),
                          (box[2][0], box[2][1]), (box[3][0], box[3][1])]
            draw.polygon(box_coords, outline=color, width=3)
            
            # 텍스트 배경과 텍스트
            text_x, text_y = box[0][0], max(0, box[0][1] - 30)
            text_content = f"{txt} ({score:.2f})"
            
            # 텍스트 배경
            text_bbox = draw.textbbox((text_x, text_y), text_content, font=font)
            draw.rectangle(text_bbox, fill='white', outline=color, width=2)
            draw.text((text_x, text_y), text_content, fill=color, font=font)
    
    return result_img, txts, scores, ocr_time

def main():
    """메인 실행 함수"""
    # 이미지 파일 확인
    img_path = "1.jpeg"
    if not os.path.exists(img_path):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {img_path}")
        print("현재 디렉토리의 파일들:")
        for file in os.listdir("."):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"  - {file}")
        return
    
    print("🔍 PaddleOCR 테스트 시작")
    print("="*50)
    
    # PaddleOCR 수행
    print("\n=== PaddleOCR 수행 중... ===")
    paddle_img, paddle_txts, paddle_scores, paddle_time = visualize_paddleocr_results(
        img_path, use_angle_cls=True, use_space_char=True
    )
    
    # 결과 시각화
    plt.figure(figsize=(15, 10))
    plt.imshow(paddle_img)
    plt.title(f'PaddleOCR Result ({paddle_time:.2f}s, CPU)', fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 텍스트 추출 결과
    print("\n" + "="*50)
    print("📝 텍스트 추출 결과")
    print("="*50)
    
    print(f"\n【PaddleOCR】 ({len(paddle_txts)}개 텍스트, {paddle_time:.2f}초)")
    print("-" * 60)
    for i, (txt, score) in enumerate(zip(paddle_txts, paddle_scores)):
        print(f"{i+1:2d}: {txt}")
        print(f"    신뢰도: {score:.3f}")
        print()
    
    # 결과 이미지 저장
    paddle_img.save('paddleocr_result.jpg')
    print(f"💾 결과 이미지 저장: paddleocr_result.jpg")
    
    print(f"\n✅ PaddleOCR 테스트 완료!")
    print(f"⚡ 처리 시간: {paddle_time:.2f}초")
    print(f"🎯 감지된 텍스트: {len(paddle_txts)}개")

if __name__ == "__main__":
    main()