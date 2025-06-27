import easyocr
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import torch
import os
import time

def check_device():
    """사용 가능한 디바이스 확인"""
    if torch.backends.mps.is_available():
        device = 'mps'
        print("🚀 MPS (Metal Performance Shaders) 사용 가능!")
    elif torch.cuda.is_available():
        device = 'cuda'
        print("🚀 CUDA GPU 사용 가능!")
    else:
        device = 'cpu'
        print("💻 CPU 모드 사용")
    
    print(f"선택된 디바이스: {device}")
    return device

def visualize_easyocr_results(img_path, threshold=0.5, device='cpu'):
    """EasyOCR 결과 시각화 (GPU 지원)"""
    print(f"EasyOCR 디바이스: {device}")
    
    # GPU 사용 여부 결정
    use_gpu = device in ['mps', 'cuda']
    
    # Reader 인스턴스 생성 (GPU 지원)
    print("EasyOCR 모델 로딩 중...")
    reader = easyocr.Reader(['ko', 'en'], gpu=use_gpu)
    
    # MPS 사용 시 추가 설정
    if device == 'mps':
        try:
            torch.backends.mps.empty_cache()  # MPS 캐시 정리 (최신 버전만 지원)
        except AttributeError:
            pass  # 구버전에서는 무시
    
    # 이미지 읽기
    pil_img = Image.open(img_path)
    
    # OCR 수행
    print("EasyOCR 텍스트 인식 중...")
    start_time = time.time()
    result = reader.readtext(img_path)
    ocr_time = time.time() - start_time
    
    print(f"OCR 처리 시간: {ocr_time:.2f}초")
    
    # 신뢰도 기준으로 필터링
    filtered_result = [r for r in result if r[2] >= threshold]
    
    print(f"전체 감지된 텍스트: {len(result)}개")
    print(f"신뢰도 {threshold} 이상: {len(filtered_result)}개")
    
    # 결과 추출
    boxes = [r[0] for r in filtered_result]
    txts = [r[1] for r in filtered_result]
    scores = [r[2] for r in filtered_result]
    
    # 시각화
    img_with_boxes = pil_img.copy()
    draw = ImageDraw.Draw(img_with_boxes)
    
    # 폰트 설정
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
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
    
    return img_with_boxes, txts, scores, ocr_time

def main():
    """메인 실행 함수"""
    # 이미지 파일 확인
    img_path = "1.jpeg"
    if not os.path.exists(img_path):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {img_path}")
        return
    
    print("🔍 EasyOCR 테스트 시작")
    print("="*50)
    
    # 디바이스 확인
    device = check_device()
    print("="*50)
    
    # EasyOCR 수행
    print("\n=== EasyOCR 수행 중... ===")
    easy_img, easy_txts, easy_scores, easy_time = visualize_easyocr_results(
        img_path, threshold=0.5, device=device
    )
    
    # 결과 시각화
    plt.figure(figsize=(15, 10))
    plt.imshow(easy_img)
    plt.title(f'EasyOCR Result ({easy_time:.2f}s, {device.upper()})', fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 텍스트 추출 결과
    print("\n" + "="*50)
    print("📝 텍스트 추출 결과")
    print("="*50)
    
    print(f"\n【EasyOCR】 ({len(easy_txts)}개 텍스트, {easy_time:.2f}초)")
    print("-" * 60)
    for i, (txt, score) in enumerate(zip(easy_txts, easy_scores)):
        print(f"{i+1:2d}: {txt}")
        print(f"    신뢰도: {score:.3f}")
        print()
    
    # 결과 이미지 저장
    easy_img.save('easyocr_result.jpg')
    print(f"💾 결과 이미지 저장: easyocr_result.jpg")
    
    # 메모리 정리
    if device == 'mps':
        try:
            torch.backends.mps.empty_cache()
        except AttributeError:
            pass  # 구버전에서는 무시
    elif device == 'cuda':
        torch.cuda.empty_cache()
    
    print(f"\n✅ EasyOCR 테스트 완료!")
    print(f"⚡ 처리 시간: {easy_time:.2f}초")
    print(f"🎯 감지된 텍스트: {len(easy_txts)}개")

if __name__ == "__main__":
    main()