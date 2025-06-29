import cv2
from PIL import Image
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import DBSCAN

def load_image_as_array(img_path="", gray=False):
    img_path = str(img_path)

    if not gray:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    return img


def save_image(img, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # PIL.Image일 경우 numpy 배열로 변환
    if isinstance(img, Image.Image):
        img = np.array(img)

    if img.ndim == 3:
        cv2.imwrite(filename=str(path), img=img[:, :, ::-1], params=[cv2.IMWRITE_JPEG_QUALITY, 100])
    elif img.ndim == 2:
        cv2.imwrite(filename=str(path), img=img, params=[cv2.IMWRITE_JPEG_QUALITY, 100])

def show_image(img1, img2=None, alpha=0.5):
    plt.figure(figsize=(11, 9))
    plt.imshow(img1)
    if img2 is not None:
        plt.imshow(img2, alpha=alpha)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def convert_to_pil(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return img


def convert_to_array(img):
    img = np.array(img)
    return img


def draw_easyocr_result(img, bboxes):
    img_copied = convert_to_pil(img.copy())
    draw = ImageDraw.Draw(img_copied)

    for bbox_points, text, confidence in bboxes:
        x_coords = [point[0] for point in bbox_points]
        y_coords = [point[1] for point in bbox_points]
        
        xmin = int(min(x_coords))
        ymin = int(min(y_coords))
        xmax = int(max(x_coords))
        ymax = int(max(y_coords))

        # 바운딩 박스 그리기
        draw.rectangle(xy=(xmin, ymin, xmax, ymax), outline=(255, 0, 0), width=2)

        # 텍스트 + 신뢰도 조합
        label = f"{text} ({confidence:.2f})"

        # 폰트 설정
        try:
            font = ImageFont.truetype("fonts/NanumSquareNeo-bRg.ttf", size=22)
        except:
            font = ImageFont.load_default()

        # 텍스트 표시
        draw.text(
            xy=(xmin, ymin - 4),
            text=label,
            fill=(255, 0, 0),
            font=font,
            anchor="ls"
        )

    return img_copied


def get_image_cropped_by_rectangle(img, xmin, ymin, xmax, ymax):
    if img.ndim == 3:
        return img[ymin: ymax, xmin: xmax, :]
    else:
        return img[ymin: ymax, xmin: xmax]

# ------------------------------
# 말풍선 병합용 DBSCAN 클러스터링
# ------------------------------
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

def draw_merged_balloons(img, merged_results):
    """
    병합된 말풍선 결과를 시각화합니다.
    merged_results: [[x, y, w, h, text, confidence], ...]
    """
    img_copied = convert_to_pil(img.copy())
    draw = ImageDraw.Draw(img_copied)

    try:
        font = ImageFont.truetype("fonts/NanumSquareNeo-bRg.ttf", size=22)
    except:
        font = ImageFont.load_default()

    for x, y, w, h, text, conf in merged_results:
        # 바운딩 박스
        draw.rectangle([x, y, x + w, y + h], outline=(0, 128, 0), width=3)

        # 텍스트와 신뢰도 표시
        label = f"{text} ({conf:.2f})"
        draw.text((x, y - 4), label, fill=(0, 128, 0), font=font, anchor="ls")

    return img_copied