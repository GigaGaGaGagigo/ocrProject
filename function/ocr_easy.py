import easyocr
import os
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image


# easyocr 분석 및 말풍선 단위 클러스터링

# ✅ 상대 경로로 수정
from .process_images_sb import cluster_boxes_edge_distance, merge_clusters
from db.crawl_sql import CutImage, Dialogue

# ✅ Fine-tuned EasyOCR 모델 로드
reader = easyocr.Reader(
    ['ko', 'en'],
    model_storage_directory="./.EasyOCR/model",
    recognizer='finetuned.pth',
    detector='finetuned.pth'
)

# 🧠 1. Streamlit 용: 이미지 하나 OCR + 병합
def analyze_image(image_path):
    image = cv2.imread(image_path)
    result = reader.readtext(image)

    # 말풍선 병합용 박스 포맷 변환
    easy_boxes = []
    for r in result:
        box = r[0]
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = box
        x_min, y_min = int(min(x1, x2, x3, x4)), int(min(y1, y2, y3, y4))
        x_max, y_max = int(max(x1, x2, x3, x4)), int(max(y1, y2, y3, y4))
        w, h = x_max - x_min, y_max - y_min
        easy_boxes.append([x_min, y_min, w, h, r[1], r[2]])

    # 클러스터링 + 병합
    clusters = cluster_boxes_edge_distance(easy_boxes, eps=25)
    merged = merge_clusters(easy_boxes, clusters)

    return result, merged  # 원본 결과와 병합 결과 둘 다 반환

def analyze_image_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(image)

        result = reader.readtext(image_np)

        # 말풍선 병합용 박스 포맷 변환
        easy_boxes = []
        for r in result:
            box = r[0]
            (x1, y1), (x2, y2), (x3, x3), (x4, y4) = box
            x_min, y_min = int(min(x1, x2, x3, x4)), int(min(y1, y2, y3, y4))
            x_max, y_max = int(max(x1, x2, x3, x4)), int(max(y1, y2, y3, y4))
            w, h = x_max - x_min, y_max - y_min
            easy_boxes.append([x_min, y_min, w, h, r[1], r[2]])

        clusters = cluster_boxes_edge_distance(easy_boxes, eps=25)
        merged = merge_clusters(easy_boxes, clusters)

        return result, merged

    except Exception as e:
        print(f"[❌ URL OCR 실패]: {e}")
        return [], []


# 💾 2. DB 저장용: episode_id 기준 컷 이미지 전체 분석
def run_easyocr_and_save(session, episode_id: int):
    cuts = session.query(CutImage).filter_by(episode_id=episode_id).order_by(CutImage.cut_number).all()

    for cut in cuts:
        if not os.path.exists(cut.image_path):
            print(f"이미지 없음: {cut.image_path}")
            continue

        image = cv2.imread(cut.image_path)
        results = reader.readtext(image)

        # 말풍선 병합용 box 포맷 변환
        easy_boxes = []
        for r in results:
            box = r[0]
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = box
            x_min, y_min = int(min(x1, x2, x3, x4)), int(min(y1, y2, y3, y4))
            x_max, y_max = int(max(x1, x2, x3, x4)), int(max(y1, y2, y3, y4))
            w, h = x_max - x_min, y_max - y_min
            easy_boxes.append([x_min, y_min, w, h, r[1], r[2]])

        clusters = cluster_boxes_edge_distance(easy_boxes, eps=25)
        merged_results = merge_clusters(easy_boxes, clusters)

        for idx, (x, y, w, h, text, conf) in enumerate(merged_results):
            dialogue = Dialogue(
                cut_image_id=cut.id,
                content=text.strip(),
                type="balloon",
                sequence=idx + 1,
                speaker_id=None
            )
            session.add(dialogue)

    session.commit()
    print(f"✅ [EasyOCR 저장 완료] episode_id={episode_id}")