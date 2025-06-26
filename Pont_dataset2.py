from PIL import Image, ImageDraw, ImageFont
import random
import pandas as pd
from tqdm import tqdm
import os # os 모듈 추가

# --- 설정 ---
FONT_PATH = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\fonts\NanumGothic.otf"
IMAGE_WIDTH = 200
IMAGE_HEIGHT = 80
FONT_SIZE_MIN = 35
FONT_SIZE_MAX = 45

# 출력 디렉토리 및 레이블 파일 경로 (이전 셀과 동일해야 함)
OUTPUT_DIR = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\generated_data"
LABELS_FILE_PATH = os.path.join(OUTPUT_DIR, "labels.csv")

# --- 이미 데이터가 생성되었는지 다시 확인하고 건너뛰기 ---
if os.path.exists(LABELS_FILE_PATH) and os.path.exists(os.path.join(OUTPUT_DIR, "images")):
    print("INFO: 레이블 파일과 이미지 폴더가 이미 존재하므로 이미지 생성 단계를 건너뜁니다.")
    # 다음 단계를 위해 char_list를 다시 로드하거나 정의해야 할 수 있습니다.
    # 여기서는 건너뛰는 메시지만 출력하고 실행하지 않습니다.
else:
    # 데이터 저장을 위한 리스트
    data = []

    # char_list가 이전 셀에서 정의되지 않았을 경우 (이전 셀이 건너뛰었을 경우) 다시 로드
    char_file_path = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\chars.txt"
    if not 'char_list' in locals() or not char_list:
         if os.path.exists(char_file_path):
              with open(char_file_path, "r", encoding="utf-8") as f:
                  loaded_chars_string = f.read()
              char_list = sorted(list(set(loaded_chars_string)))
              print(f"INFO: '{char_file_path}'에서 문자 목록을 로드했습니다. 총 {len(char_list)}개")
         else:
              print(f"ERROR: 문자 목록 파일 '{char_file_path}'을 찾을 수 없습니다. 이전 단계를 먼저 실행해주세요.")
              char_list = [] # 빈 리스트로 설정하여 아래 반복문이 실행되지 않도록 함

    print("글자 이미지 생성을 시작합니다...")

    # tqdm을 사용하여 진행 상황 표시
    for i, char in enumerate(tqdm(char_list)):
        try:
            # 랜덤 폰트 크기 및 배경색 설정
            font_size = random.randint(FONT_SIZE_MIN, FONT_SIZE_MAX)
            font = ImageFont.truetype(FONT_PATH, font_size)

            # 텍스트 크기 계산
            text_bbox = font.getbbox(char)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # 이미지 크기 설정 (텍스트 크기보다 여유있게)
            img_width = text_width + 20
            img_height = text_height + 20

            # 회색조(Grayscale) 이미지 생성
            image = Image.new('L', (img_width, img_height), color=random.randint(220, 255))
            draw = ImageDraw.Draw(image)

            # 텍스트 위치 계산 및 그리기
            x = (img_width - text_width) / 2
            y = (img_height - text_height) / 2 - text_bbox[1] # y 오프셋 보정
            draw.text((x, y), char, fill=random.randint(0, 50), font=font)

            # 파일명 및 저장
            img_filename = f"img_{i+1}.png"
            img_path = os.path.join(OUTPUT_DIR, "images", img_filename)
            image.save(img_path)

            # 레이블 데이터 추가 (상대 경로 사용)
            data.append([f"images/{img_filename}", char])

        except Exception as e:
            print(f"'{char}' 문자 생성 중 오류 발생: {e}")

    # DataFrame 생성 및 CSV 파일로 저장
    if data: # 데이터가 생성된 경우에만 저장
        df = pd.DataFrame(data, columns=['filename', 'words'])
        labels_path = os.path.join(OUTPUT_DIR, "labels.csv")
        df.to_csv(labels_path, index=False, sep='\t', header=False, encoding='utf-8')

        print(f"\n총 {len(data)}개의 이미지 및 레이블 생성 완료!")
        print(f"이미지 저장 폴더: {os.path.join(OUTPUT_DIR, 'images')}")
        print(f"레이블 파일: {labels_path}")
    else:
        print("\n데이터 생성에 실패했거나 건너뛰었습니다.")