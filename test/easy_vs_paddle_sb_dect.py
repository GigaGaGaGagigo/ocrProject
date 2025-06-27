import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import DBSCAN
import easyocr
from paddleocr import PaddleOCR, draw_ocr

"""
easyocr과 paddle ocr의 말풍선 병합 과정의 성능을 비교하는 코드입니다. 
""" 

# === [공통 함수] 말풍선 병합용 클러스터링 ===

def box_edge_distance(b1, b2):
    x1_min, y1_min, x1_max, y1_max = b1[0], b1[1], b1[0]+b1[2], b1[1]+b1[3]
    x2_min, y2_min, x2_max, y2_max = b2[0], b2[1], b2[0]+b2[2], b2[1]+b2[3]
    dx = max(0, max(x1_min - x2_max, x2_min - x1_max))
    dy = max(0, max(y1_min - y2_max, y2_min - y1_max))
    return np.hypot(dx, dy)

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

def merge_clusters(boxes, clusters):
    final_result = []
    for c in clusters:
        sub_result = [boxes[i] for i in c]
        sub_result = sorted(sub_result, key=lambda b: (b[1], b[0]))
        x1 = min(r[0] for r in sub_result)
        y1 = min(r[1] for r in sub_result)
        x2 = max(r[0]+r[2] for r in sub_result)
        y2 = max(r[1]+r[3] for r in sub_result)
        w, h = x2 - x1, y2 - y1
        text = " ".join([r[4] for r in sub_result])
        conf = np.mean([r[5] for r in sub_result])
        final_result.append([x1, y1, w, h, text.strip(), conf])
    return final_result

# === [1] 이미지 로딩 ===
img_path = "1.JPEG" # 실제 사용 이미지로 입력하세요
pil_img = Image.open(img_path).convert("RGB")
img_np = np.array(pil_img)

# === [2] EasyOCR 실행 ===
reader = easyocr.Reader(['ko', 'en'], gpu=False)
easy_result = reader.readtext(img_np)

easy_boxes = []
for i, r in enumerate(easy_result):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = r[0]
    x_min, y_min = min(x1, x2, x3, x4), min(y1, y2, y3, y4)
    x_max, y_max = max(x1, x2, x3, x4), max(y1, y2, y3, y4)
    w, h = x_max - x_min, y_max - y_min
    easy_boxes.append([int(x_min), int(y_min), int(w), int(h), r[1], r[2], i])

easy_clusters = cluster_boxes_edge_distance(easy_boxes, eps=25)
easy_final = merge_clusters(easy_boxes, easy_clusters)

# === [3] PaddleOCR 실행 ===
paddle_ocr = PaddleOCR(lang='korean')
paddle_result = paddle_ocr.ocr(img_path, cls=False)

paddle_boxes = []
for i, r in enumerate(paddle_result[0]):
    x1, y1 = r[0][0]
    x2, y2 = r[0][2]
    w, h = x2 - x1, y2 - y1
    text, conf = r[1]
    paddle_boxes.append([int(x1), int(y1), int(w), int(h), text, conf, i])

paddle_clusters = cluster_boxes_edge_distance(paddle_boxes, eps=25)
paddle_final = merge_clusters(paddle_boxes, paddle_clusters)

# === [4] 시각화 비교 ===
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
# window인 경우 폰트경로 바꾸기 (예: "malgun.ttf" on Windows)
font = ImageFont.truetype(font_path, 16)

def draw_result_on_image(base_img, results, title):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    for box in results:
        x, y, w, h, text, conf = box
        draw.rectangle([(x, y), (x+w, y+h)], outline="red", width=2)
        draw.text((x, y - 20), text, fill="blue", font=font)
    return img

easy_img = draw_result_on_image(pil_img, easy_final, "EasyOCR")
paddle_img = draw_result_on_image(pil_img, paddle_final, "PaddleOCR")

# 나란히 보여주기
fig, axes = plt.subplots(1, 2, figsize=(16, 10))
axes[0].imshow(easy_img)
axes[0].set_title("EasyOCR result")
axes[0].axis("off")
axes[1].imshow(paddle_img)
axes[1].set_title("PaddleOCR result")
axes[1].axis("off")
plt.tight_layout()
plt.show()

# === [5] 텍스트 비교 출력 ===
print("\n=== EasyOCR 말풍선 단위 텍스트 ===")
for i, r in enumerate(easy_final):
    print(f"{i+1}: {r[4]} (신뢰도: {r[5]:.3f})")

print("\n=== PaddleOCR 말풍선 단위 텍스트 ===")
for i, r in enumerate(paddle_final):
    print(f"{i+1}: {r[4]} (신뢰도: {r[5]:.3f})")