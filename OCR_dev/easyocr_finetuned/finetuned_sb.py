import easyocr
import cv2
import numpy as np
import os

# eacyocr에 파인튜닝된 모델을 바탕으로 말풍선 단위 텍스트를 추출하는 코드

from process_images_sb import (
    draw_easyocr_result,  # 개별 텍스트 박스 시각화
    save_image,            # 이미지 저장
    cluster_boxes_edge_distance,  # DBSCAN 클러스터링
    merge_clusters,              # 병합 결과 생성
    draw_merged_balloons         # 말풍선 병합 시각화
)

print("현재 작업 디렉토리:", os.getcwd())

# [1] Fine-tuned 모델 로드
reader = easyocr.Reader(
    ['ko', 'en'],
    model_storage_directory='./.EasyOCR/model',
    detector='finetuned.pth',
    recognizer='finetuned.pth'
)

# [2] 이미지 로딩
image_path = './dataset/sample/실제파일명.jpeg' # 해당경로에 이미지 입력 및 실제 파일명으로 수정  
image = cv2.imread(image_path)

# [3] 텍스트 인식
result = reader.readtext(image)

# [4] 결과 출력 (개별 항목)
print("📌 개별 텍스트 인식 결과:")
for detection in result:
    print(detection)

# [5] 개별 바운딩 박스 시각화
drawn_individual = draw_easyocr_result(img=image, bboxes=result)
save_image(drawn_individual, "result_individual.jpg")

# [6] 말풍선 병합을 위한 좌표 및 텍스트 추출
easy_boxes = []
for r in result:
    box = r[0]
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = box
    x_min, y_min = int(min(x1, x2, x3, x4)), int(min(y1, y2, y3, y4))
    x_max, y_max = int(max(x1, x2, x3, x4)), int(max(y1, y2, y3, y4))
    w, h = x_max - x_min, y_max - y_min
    easy_boxes.append([x_min, y_min, w, h, r[1], r[2]])

# [7] DBSCAN 클러스터링 + 병합
clusters = cluster_boxes_edge_distance(easy_boxes, eps=25)
merged_results = merge_clusters(easy_boxes, clusters)

# [8] 병합 결과 시각화
drawn_merged = draw_merged_balloons(image, merged_results)
save_image(drawn_merged, "result_merged.jpg")

# ✅ [9] 말풍선 단위 텍스트 출력
print("\n🗨️ 말풍선 단위 병합 결과:")
for idx, (x, y, w, h, text, conf) in enumerate(merged_results):
    print(f"{idx+1:02d}. \"{text}\"  (신뢰도 평균: {conf:.2f})")