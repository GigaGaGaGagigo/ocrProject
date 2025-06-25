
import os
import lmdb
import cv2
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def checkImageIsValid(imageBin):
    """OpenCV를 사용해 이미지가 유효한지 확인"""
    if imageBin is None:
        return False
    try:
        imageBuf = np.frombuffer(imageBin, dtype=np.uint8)
        img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return False
        imgH, imgW = img.shape[0], img.shape[1]
        if imgH * imgW == 0:
            return False
    except Exception as e:
        print(f"이미지 유효성 검사 중 오류: {e}")
        return False
    return True


def writeCache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            txn.put(k, v)


def createDataset(outputPath, imagePathList, labelList, lexiconList=None, checkValid=True):
    """
    LMDB 데이터셋을 생성합니다.
    outputPath: LMDB 파일이 저장될 폴더 경로
    imagePathList: 이미지 파일 경로 리스트
    labelList: 정답 텍스트 리스트
    """
    assert len(imagePathList) == len(labelList)
    nSamples = len(imagePathList)
    
    # map_size를 넉넉하게 설정 (10GB)
    env = lmdb.open(outputPath, map_size=1099511627776)
    cache = {}
    cnt = 1
    
    for i in range(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        
        if not os.path.exists(imagePath):
            print(f'{imagePath} does not exist')
            continue

        with open(imagePath, 'rb') as f:
            imageBin = f.read()
        
        if checkValid and not checkImageIsValid(imageBin):
            print(f'{imagePath} is not a valid image')
            continue

        imageKey = f'image-{cnt:09d}'.encode()
        labelKey = f'label-{cnt:09d}'.encode()
        cache[imageKey] = imageBin
        cache[labelKey] = label.encode()

        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print(f'Written {cnt} / {nSamples}')
        
        cnt += 1
        
    cache['num-samples'.encode()] = str(cnt - 1).encode()
    writeCache(env, cache)
    print(f'Created dataset with {cnt - 1} samples')


if __name__ == '__main__':
    # --- 설정 ---
    IMAGE_DIR = './data/webtoon_train_images/'
    LABEL_CSV_PATH = './data/train_labels.csv'
    TRAIN_OUTPUT_PATH = './data/lmdb_output/train'
    VALID_OUTPUT_PATH = './data/lmdb_output/validation'

    # 출력 폴더 생성
    os.makedirs(TRAIN_OUTPUT_PATH, exist_ok=True)
    os.makedirs(VALID_OUTPUT_PATH, exist_ok=True)

    # 레이블 파일 로드
    df = pd.read_csv(LABEL_CSV_PATH)
    df.dropna(inplace=True) # 누락된 레이블 제거
    
    # 이미지 경로와 레이블 리스트 생성
    image_paths = [os.path.join(IMAGE_DIR, fname) for fname in df['filename']]
    labels = df['text'].tolist()

    # 훈련/검증 데이터 분리 (9:1)
    img_train, img_val, lbl_train, lbl_val = train_test_split(
        image_paths, labels, test_size=0.1, random_state=42
    )

    print("--- 훈련용 LMDB 데이터셋 생성 시작 ---")
    createDataset(TRAIN_OUTPUT_PATH, img_train, lbl_train)
    
    print("\n--- 검증용 LMDB 데이터셋 생성 시작 ---")
    createDataset(VALID_OUTPUT_PATH, img_val, lbl_val)