import os
import shutil
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm


# --- 설정 ---
BASE_DATA_DIR = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\generated_data"
TRAIN_DIR = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\train_data"
VALID_DIR = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\valid_data"

# 기존 폴더 삭제 및 재생성
for d in [TRAIN_DIR, VALID_DIR]:
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "images"))

# 레이블 파일 읽기
df = pd.read_csv(os.path.join(BASE_DATA_DIR, "labels.csv"), sep='\t', header=None, encoding='utf-8')
df.columns = ['filepath', 'text']

# 학습/검증 데이터 분리
train_df, valid_df = train_test_split(df, test_size=0.1, random_state=42)

print(f"학습 데이터: {len(train_df)}개, 검증 데이터: {len(valid_df)}개")

# 파일 복사 및 새 labels.csv 생성 함수
def setup_dataset(df, dest_dir):
    new_rows = []
    labels_path = os.path.join(dest_dir, "labels.csv")
    img_dest_dir = os.path.join(dest_dir, "images")

    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Setting up {os.path.basename(dest_dir)}"):
        # 원본 이미지 경로
        src_img_path = os.path.join(BASE_DATA_DIR, row['filepath'])
        # 대상 이미지 경로
        dest_img_path = os.path.join(img_dest_dir, os.path.basename(row['filepath']))

        # 이미지 복사
        shutil.copy(src_img_path, dest_img_path)

        # 새 레이블 파일에 쓸 내용 추가 (경로명 변경)
        new_filepath = os.path.join("images", os.path.basename(row['filepath']))
        new_rows.append({'filepath': new_filepath, 'text': row['text']})

    # 새 labels.csv 파일 저장
    new_df = pd.DataFrame(new_rows)
    new_df.to_csv(labels_path, sep='\t', index=False, header=False, encoding='utf-8')
    print(f"{dest_dir} 설정 완료.")

# 학습 및 검증 데이터셋 설정 실행
setup_dataset(train_df, TRAIN_DIR)
setup_dataset(valid_df, VALID_DIR)