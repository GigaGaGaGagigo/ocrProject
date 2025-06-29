import easyocr # easycor 수행 라이브러리
import cv2 # OPEN cv 라이브러리 (이미지 읽기, 쓰기) 
import numpy as np # 수치 계산 (바운딩 박스 처리를 등에 유용)

import os
print("현재 작업 디렉토리:", os.getcwd())

from process_images import (
    draw_easyocr_result, # ocr결과(바운딩 박스) 시각화
    save_image # 처리한 이미지 파일로 저장 
)

# 파인튜닝된 모델 파일들을 지정
reader = easyocr.Reader( # 객체 생성(추론 준비)
    ['ko', 'en'],  # 언어 설정
    model_storage_directory='./.EasyOCR/model',  # 커스텀 모델 저장 경로(한글 학습 모델 저장)
    detector='finetuned.pth',  # 커스텀 detector 모델 (fine-tune된 모델의 가중치 지정, 텍스트 감지)
    recognizer='finetuned.pth'  # 커스텀 recognizer 모델 (fine-tune된 모델의 가중치 지정, 텍스트 인식)
) # easyocr의 텍스트 인식은 텍스트 감지, 인식 두단계로 진행됨 

# 이미지 경로 지정
image_path = './dataset/sample/실제파일명.jpeg' # 해당경로에 이미지 입력 및 실제 파일명으로 수정 

# 이미지 읽기
image = cv2.imread(image_path) # open cv로 이미지 읽기

# 텍스트 인식
result = reader.readtext(image) # (추론 수행)
# eacyocr을 활용해 이미지에서 텍스트 감지하고 인식함 
# 반환결과 리스트 형태: 각 항목은 (바운딩 박스, 텍스트, 신뢰도 점수) 튜플

print(result) # (추론결과) 텍스트 인식 전체 결과를 출력  

# 결과 출력 (감지된 텍스트 개별항목들을 출력)
for detection in result: 
    print(detection)

# 바운딩 박스 등의 ocr 결과를 원본 이미지에 시각화 
drawn = draw_easyocr_result(img=image, bboxes=result)
save_image(img=drawn, path='result.jpg') # 이미지 결과 저장 필요하면 활용 (필요없을 시 주석처리)

# # 결과 이미지에 텍스트 추가
# for detection in result:
#     bbox, text, score = detection
    
#     # bbox를 정수형 numpy 배열로 변환
#     bbox = np.array(bbox, dtype=np.int32)
    
#     # 바운딩 박스의 최소/최대 좌표 계산
#     x_min = int(min(bbox[:, 0]))
#     y_min = int(min(bbox[:, 1]))
#     x_max = int(max(bbox[:, 0]))
#     y_max = int(max(bbox[:, 1]))
    
#     # 사각형 그리기 (좌상단, 우하단 좌표 사용)
#     cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    
#     # 텍스트 추가 (좌상단 좌표 사용)
#     cv2.putText(image, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# # 결과 이미지 저장
# cv2.imwrite('result.jpg', image)



