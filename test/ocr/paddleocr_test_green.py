from paddleocr import PaddleOCR, draw_ocr
import paddle
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import time


def visualize_paddleocr_results(img_path, device="cpu", use_angle_cls=True, use_space_char=True):
    """PaddleOCR 결과 시각화 (디바이스 선택 가능 + mps 대응)"""

    # 디바이스 설정 로직
    if device == "mps":
        print("🔧 MPS 디바이스 요청됨 → paddle.set_device('cpu') + use_gpu=True 적용")
        paddle.set_device("cpu")  # 직접 mps는 안됨, 내부적으로 처리됨
        use_gpu_flag = True
        device_name = "MPS (Apple Silicon)"
    elif device == "gpu":
        try:
            paddle.set_device("gpu")
            use_gpu_flag = True
            device_name = "GPU"
        except Exception as e:
            print(f"❌ GPU 설정 오류: {e}")
            print("➡️ CPU로 대체합니다.")
            paddle.set_device("cpu")
            use_gpu_flag = False
            device_name = "CPU (fallback)"
    else:
        paddle.set_device("cpu")
        use_gpu_flag = False
        device_name = "CPU"

    print(f"✅ PaddleOCR 디바이스 설정됨: {device_name}")
    
    # PaddleOCR 초기화
    print("PaddleOCR 모델 로딩 중...")
    try:
        ocr = PaddleOCR(
            lang="korean",
            use_gpu=use_gpu_flag,
            show_log=False,
            use_angle_cls=use_angle_cls,
            use_space_char=use_space_char
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
    
    if result[0] is None:
        print("PaddleOCR: 텍스트를 찾을 수 없습니다.")
        return pil_img, [], [], ocr_time
    
    boxes = [line[0] for line in result[0]]
    txts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]
    
    # 시각화
    try:
        font_paths = [
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
        
        font_path = next((fp for fp in font_paths if os.path.exists(fp)), None)
        result_np = draw_ocr(img, boxes, txts, scores, font_path=font_path)
        result_img = Image.fromarray(result_np)
    except Exception as e:
        print(f"draw_ocr 오류: {e}")
        print("수동 시각화로 대체...")
        result_img = pil_img.copy()
        draw = ImageDraw.Draw(result_img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/AppleGothic.ttf", 20)
        except:
            font = ImageFont.load_default()
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
        for i, (box, txt, score) in enumerate(zip(boxes, txts, scores)):
            color = colors[i % len(colors)]
            box = np.array(box).astype(np.int32)
            draw.polygon([(x, y) for x, y in box], outline=color, width=3)
            text = f"{txt} ({score:.2f})"
            x, y = box[0]
            y = max(0, y - 30)
            bbox = draw.textbbox((x, y), text, font=font)
            draw.rectangle(bbox, fill='white', outline=color)
            draw.text((x, y), text, fill=color, font=font)
    
    return result_img, txts, scores, ocr_time, device_name


def main():
    img_path = "test.jpeg"
    if not os.path.exists(img_path):
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {img_path}")
        print("현재 디렉토리의 이미지 목록:")
        for file in os.listdir("."):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                print(f"  - {file}")
        return

    # 사용할 디바이스 선택: "cpu", "gpu", "mps"
    selected_device = "mps"  # ← 여기만 바꾸면 됩니다!

    print(f"\n🔍 PaddleOCR 실행 (디바이스: {selected_device.upper()})")
    print("="*50)
    
    paddle_img, txts, scores, elapsed, device_name = visualize_paddleocr_results(
        img_path, device=selected_device
    )
    
    # 결과 시각화
    plt.figure(figsize=(15, 10))
    plt.imshow(paddle_img)
    plt.title(f'PaddleOCR Result ({elapsed:.2f}s, {device_name})')
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    # 텍스트 출력
    print("\n📝 추출된 텍스트")
    print("="*50)
    for i, (txt, score) in enumerate(zip(txts, scores)):
        print(f"{i+1:2d}: {txt} (score={score:.2f})")
    
    # 결과 저장
    result_filename = f'paddleocr_result_{selected_device}.jpg'
    paddle_img.save(result_filename)
    print(f"\n💾 결과 이미지 저장됨: {result_filename}")
    print(f"⚡ 처리 시간: {elapsed:.2f}초")

if __name__ == "__main__":
    main()