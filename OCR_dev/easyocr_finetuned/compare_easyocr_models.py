import easyocr  # EasyOCR 수행 라이브러리
import cv2  # OpenCV 라이브러리 (이미지 읽기, 시각화)
import numpy as np  # 수치 계산 (배열, 바운딩 박스 등)
import os

from process_images import draw_easyocr_result, save_image  # 시각화 및 저장 함수

# 기본 easyocr과 파인튜닝 easyocr의 성능을 비교하는 함수입니다. 

# ------------------------------
# 설정
# ------------------------------
image_path = './dataset/sample/실제파일명.jpeg' # 해당경로에 이미지 입력 및 실제 파일명으로 수정 
model_path = './finetuned/finetuned.pth'  # Fine-tuned recognizer 경로
model_dir = './.EasyOCR/model'  # EasyOCR에서 커스텀 모델을 읽을 디렉토리

print("현재 작업 디렉토리:", os.getcwd())

# ------------------------------
# 이미지 로드
# ------------------------------
image = cv2.imread(image_path)

# ------------------------------
# 기본 EasyOCR 모델 추론
# ------------------------------
default_reader = easyocr.Reader(['ko', 'en'], gpu=False)
default_result = default_reader.readtext(image)

drawn_default = draw_easyocr_result(img=image.copy(), bboxes=default_result)

# ------------------------------
# Fine-tuned recognizer만 적용한 모델 추론
# ------------------------------
fine_tuned_reader = easyocr.Reader(
    ['ko', 'en'],
    model_storage_directory=model_dir,
    # detector=False,디텍터 감지 기능 생략해서 기본기능 사용하려 했으나 오류나서 생략하는 방법으로 사용
    recognizer='finetuned.pth'
)
fine_tuned_result = fine_tuned_reader.readtext(image)

drawn_finetuned = draw_easyocr_result(img=image.copy(), bboxes=fine_tuned_result)

# ------------------------------
# 결과 비교 출력
# ------------------------------
print("\n📌 [기본 EasyOCR 결과]")
for detection in default_result:
    print(detection)

print("\n📌 [Fine-tuned recognizer 결과]")
for detection in fine_tuned_result:
    print(detection)

# ------------------------------
# 결과 이미지 좌우 비교 저장
# ------------------------------
side_by_side = np.concatenate((drawn_default, drawn_finetuned), axis=1)
save_image(img=side_by_side, path='compare_result_side_by_side.jpg')