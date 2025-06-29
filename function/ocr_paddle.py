from paddleocr import PaddleOCR
import numpy as np
import cv2
import os
from sklearn.cluster import DBSCAN
from db.crawl_sql import CutImage, Dialogue
from sqlalchemy.orm import Session

# 🔧 PaddleOCR 초기화 (한글 기준)
ocr = PaddleOCR(lang="korean", use_angle_cls=True, use_gpu=False)

# PaddleOCR 분석 함수
def paddleocr_analyze(image_path):
    result = ocr.ocr(image_path, cls=False)[0]

    boxes = []
    for r in result:
        (x1, y1), (x2, y2) = r[0][0], r[0][2]
        w, h = x2 - x1, y2 - y1
        text, conf = r[1]
        boxes.append([int(x1), int(y1), int(w), int(h), text, conf])

    return boxes

# ✅ 거리 기반 박스 간 거리 계산
def box_edge_distance(b1, b2):
    x1_min, y1_min, x1_max, y1_max = b1[0], b1[1], b1[0] + b1[2], b1[1] + b1[3]
    x2_min, y2_min, x2_max, y2_max = b2[0], b2[1], b2[0] + b2[2], b2[1] + b2[3]
    dx = max(0, max(x1_min - x2_max, x2_min - x1_max))
    dy = max(0, max(y1_min - y2_max, y2_min - y1_max))
    return np.hypot(dx, dy)


# ✅ DBSCAN 클러스터링
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


# ✅ 줄 단위 정렬 및 텍스트 병합
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


# 🧠 1. Streamlit 용: 이미지 하나 분석 + 병합 텍스트 반환
def analyze_image(image_path):
    result = ocr.ocr(image_path, cls=False)[0]
    boxes = []
    for i, r in enumerate(result):
        x1, y1 = r[0][0]
        x2, y2 = r[0][2]
        w, h = x2 - x1, y2 - y1
        text, conf = r[1]
        boxes.append([int(x1), int(y1), int(w), int(h), text, conf, i])

    clusters = cluster_boxes_edge_distance(boxes, eps=25)

    final_result = []
    for cluster in clusters:
        sub_result = [boxes[i] for i in cluster]
        line_groups = group_lines(sub_result)
        line_groups = sorted(line_groups, key=lambda l: min(b[1] for b in l))

        merged_text = ''
        for line in line_groups:
            line_sorted = sorted(line, key=lambda b: b[0])
            merged_text += ' '.join(b[4] for b in line_sorted) + ' '

        x1 = min(r[0] for r in sub_result)
        y1 = min(r[1] for r in sub_result)
        x2 = max(r[0] + r[2] for r in sub_result)
        y2 = max(r[1] + r[3] for r in sub_result)
        w, h = x2 - x1, y2 - y1
        conf = np.mean([r[5] for r in sub_result])

        final_result.append([x1, y1, w, h, merged_text.strip(), conf])
    return final_result


# 💾 2. DB 저장용: 말풍선 기준 저장
def run_paddleocr_and_save(session: Session, episode_id: int):
    cuts = session.query(CutImage).filter_by(episode_id=episode_id).order_by(CutImage.cut_number).all()

    for cut in cuts:
        if not os.path.exists(cut.image_path):
            print(f"이미지 없음: {cut.image_path}")
            continue

        result = analyze_image(cut.image_path)
        for idx, (x, y, w, h, text, conf) in enumerate(result):
            dialogue = Dialogue(
                cut_image_id=cut.id,
                content=text,
                type="balloon",
                sequence=idx + 1,
                speaker_id=None
            )
            session.add(dialogue)
    session.commit()
    print(f"✅ [PaddleOCR 병합 저장 완료] episode_id={episode_id}")


# 💾 3. DB 저장용: 텍스트 단위 저장
def run_paddleocr_text_only(session: Session, episode_id: int):
    cuts = session.query(CutImage).filter_by(episode_id=episode_id).order_by(CutImage.cut_number).all()

    for cut in cuts:
        if not os.path.exists(cut.image_path):
            print(f"이미지 없음: {cut.image_path}")
            continue

        result = ocr.ocr(cut.image_path, cls=False)[0]
        for idx, r in enumerate(result):
            text, conf = r[1]
            dialogue = Dialogue(
                cut_image_id=cut.id,
                content=text.strip(),
                type="text",
                sequence=idx + 1,
                speaker_id=None
            )
            session.add(dialogue)
    session.commit()
    print(f"✅ [PaddleOCR 텍스트 단위 저장 완료] episode_id={episode_id}")