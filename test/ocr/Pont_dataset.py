import os

# --- 설정 ---
FONT_NAME = "NanumGothic.otf"  # fonts 폴더에 업로드한 폰트 파일명
FONT_PATH = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\fonts\{}".format(FONT_NAME)
OUTPUT_DIR = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\generated_data"

# 건너뛰기 조건을 위한 레이블 파일 경로
LABELS_FILE_PATH = os.path.join(OUTPUT_DIR, "labels.csv")

# --- 이미 데이터가 생성되었는지 확인 ---
if os.path.exists(LABELS_FILE_PATH) and os.path.exists(os.path.join(OUTPUT_DIR, "images")):
    print("INFO: 데이터가 이미 생성되었습니다. 이 단계는 건너뜁니다.")
    # 필요한 변수들 (char_list, char_file_path, OUTPUT_DIR)은 이전에 정의된 값을 사용하거나 다시 로드해야 할 수 있습니다.
    # 여기서는 간단히 메시지만 출력하고 다음 셀에서 실제로 파일 존재 여부를 다시 확인합니다.
else:
    print("INFO: 데이터를 생성합니다...")
    # 학습할 문자 리스트 (KS X 1001 완성형 한글 2350자 + 영문 + 숫자 + 주요 기호)
    # 필요한 문자를 추가하거나 제거할 수 있습니다.
    chars = []
    # 한글 (가 ~ 힣)
    for i in range(11172):
        chars.append(chr(0xAC00 + i))

    # 영어 대문자 및 소문자
    for i in range(26):
        chars.append(chr(ord('A') + i))
        chars.append(chr(ord('a') + i))

    # 숫자
    for i in range(10):
        chars.append(str(i))

    # 특수문자
    special_chars = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
    chars.extend(list(special_chars))

    # 중복 제거 및 정렬
    char_list = sorted(list(set(chars)))

    print(f"학습할 총 문자 수: {len(char_list)}개")
    print(f"폰트 경로: {FONT_PATH}")

    # 문자 목록을 파일로 저장 (나중에 설정 파일에서 사용)
    char_file_path = r"C:\git-practice-text\OCR\ocrProject\OCR_Custom\chars.txt"
    with open(char_file_path, "w", encoding="utf-8") as f:
        f.write("".join(char_list))

    print(f"문자 목록 파일 저장 완료: {char_file_path}")

    # 출력 폴더 생성
    os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)