# PaddleOCR 단계별 테스트
print("=== 1단계: 모듈 import 테스트 ===")
try:
    from paddleocr import PaddleOCR, draw_ocr
    print("✅ PaddleOCR import 성공")
except ImportError as e:
    print(f"❌ PaddleOCR import 실패: {e}")
    exit(1)

try:
    import easyocr
    print("✅ EasyOCR import 성공")
except ImportError as e:
    print(f"❌ EasyOCR import 실패: {e}")
    print("EasyOCR 설치: pip install easyocr")

print("\n=== 2단계: 기타 모듈 테스트 ===")
try:
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw, ImageFont
    print("✅ 기타 모듈들 import 성공")
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")

print("\n=== 3단계: PaddleOCR 초기화 테스트 ===")
try:
    # PaddleOCR 초기화 (처음 실행 시 모델 다운로드로 시간이 걸릴 수 있음)
    ocr = PaddleOCR(lang="korean", use_angle_cls=False, use_gpu=False)
    print("✅ PaddleOCR 초기화 성공")
except Exception as e:
    print(f"❌ PaddleOCR 초기화 실패: {e}")
    print("가능한 해결책:")
    print("1. 인터넷 연결 확인 (모델 다운로드 필요)")
    print("2. 의존성 패키지 재설치")

print("\n=== 4단계: EasyOCR 초기화 테스트 ===")
try:
    reader = easyocr.Reader(['ko', 'en'])
    print("✅ EasyOCR 초기화 성공")
except Exception as e:
    print(f"❌ EasyOCR 초기화 실패: {e}")

print("\n모든 테스트 완료!")