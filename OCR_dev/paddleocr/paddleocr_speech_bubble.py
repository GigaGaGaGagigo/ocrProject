from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import os

# === [1] PaddleOCR 초기화 ===
ocr = PaddleOCR(lang="korean", use_angle_cls=True, use_gpu=False)  # use_gpu=True 로 바꿔도 OK

# === [2] 이미지 경로 및 읽기 ===
img_path = "파일명입력.JPEG"  # 같은 수준 폴더 내 이미지 입력 및 실제 파일명으로 수정 
pil_img = Image.open(img_path).convert("RGB")
img = np.array(pil_img)

# === [3] OCR 수행 ===
result = ocr.ocr(img_path, cls=False)

# === [4] OCR 결과 정리 ===
boxes = []
for i, r in enumerate(result[0]):
    x1, y1 = r[0][0]
    x2, y2 = r[0][2]
    w, h = x2 - x1, y2 - y1
    text, conf = r[1]
    boxes.append([int(x1), int(y1), int(w), int(h), text, conf, i])

# === [5] 박스 간 거리 계산 함수 ===
def box_edge_distance(b1, b2):
    x1_min, y1_min, x1_max, y1_max = b1[0], b1[1], b1[0]+b1[2], b1[1]+b1[3]
    x2_min, y2_min, x2_max, y2_max = b2[0], b2[1], b2[0]+b2[2], b2[1]+b2[3]
    dx = max(0, max(x1_min - x2_max, x2_min - x1_max))
    dy = max(0, max(y1_min - y2_max, y2_min - y1_max))
    return np.hypot(dx, dy)

# === [6] DBSCAN 클러스터링 함수 ===
def cluster_boxes_edge_distance(boxes, eps=25):
    n = len(boxes)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = box_edge_distance(boxes[i], boxes[j])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d
    clustering = DBSCAN(eps=eps, min_samples=1, metric='precomputed')
    labels = clustering.fit_predict(dist_matrix)

    clusters = {}
    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(i)

    return list(clusters.values())

# === [7] 클러스터링 실행 ===
clusters = cluster_boxes_edge_distance(boxes, eps=25)

# === [8] 줄 단위 정렬 함수 ===
def group_lines(sub_result, line_tol=15):
    lines = []
    sub_result = sorted(sub_result, key=lambda b: b[1])  # y 기준 정렬
    for b in sub_result:
        placed = False
        for line in lines:
            if abs(b[1] - line[0][1]) <= line_tol:
                line.append(b)
                placed = True
                break
        if not placed:
            lines.append([b])
    return lines

# === [9] 클러스터 병합 및 정렬 개선 ===
final_result = []
for cluster in clusters:
    sub_result = [boxes[i] for i in cluster]
    line_groups = group_lines(sub_result, line_tol=15)
    line_groups = sorted(line_groups, key=lambda l: min(b[1] for b in l))  # 줄 순서 정렬

    merged_text = ''
    for line in line_groups:
        line_sorted = sorted(line, key=lambda b: b[0])  # 줄 안에서 왼→오 정렬
        merged_text += ' '.join(b[4] for b in line_sorted) + ' '

    x1 = min(r[0] for r in sub_result)
    y1 = min(r[1] for r in sub_result)
    x2 = max(r[0] + r[2] for r in sub_result)
    y2 = max(r[1] + r[3] for r in sub_result)
    w, h = x2 - x1, y2 - y1
    conf = np.mean([r[5] for r in sub_result])

    final_result.append([x1, y1, w, h, merged_text.strip(), conf])

# === [10] 시각화 준비 ===
draw_boxes = [[(b[0], b[1]), (b[0]+b[2], b[1]), (b[0]+b[2], b[1]+b[3]), (b[0], b[1]+b[3])] for b in final_result]
draw_texts = [b[4] for b in final_result]
draw_scores = [b[5] for b in final_result]

result_img_np = draw_ocr(
    img, draw_boxes, draw_texts, draw_scores,
    font_path="/System/Library/Fonts/Supplemental/AppleGothic.ttf"  # Mac용 폰트
)

# === [11] 이미지 결과 출력 ===
result_img = Image.fromarray(result_img_np)
plt.figure(figsize=(12, 8))
plt.imshow(result_img)
plt.axis('off')
plt.title('PaddleOCR speech bubble merge result')
plt.show()

# === [12] 텍스트 출력 ===
print("\n=== 추출된 말풍선 단위 텍스트 ===")
for i, res in enumerate(final_result):
    print(f"{i+1}: {res[4]} (신뢰도 평균: {res[5]:.3f})")