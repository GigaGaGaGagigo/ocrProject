import easyocr 
import cv2
import matplotlib.pyplot as plt 

# Reader 인스턴스 생성
reader = easyocr.Reader(['ko', 'en'])  # 한글과 영어 인식
THRESHOLD = 0.5  # 컨피던스 기준, 추출하고 싶은 값에 맞게 수정 

def read(img_path):
    """
    이미지 경로를 바탕으로 특정 컨피던스 이상의 인식률을 보인 텍스트만 추출,
    추출된 부분을 네모박스로 표시하는 함수 
    """
    import numpy as np
    from PIL import Image
    
    # 파일 존재 여부 먼저 확인
    if not os.path.exists(img_path):
        print(f"파일이 존재하지 않습니다: {img_path}")
        return
    
    # 이미지 로드 (여러 방법 시도)
    img = None
    
    # 방법 1: OpenCV로 직접 읽기
    try:
        img = cv2.imread(img_path)
        if img is not None:
            print("OpenCV로 이미지 로드 성공")
        else:
            raise Exception("OpenCV imread failed")
    except:
        print("OpenCV 직접 로드 실패, PIL로 시도중...")
        
        # 방법 2: PIL로 읽고 OpenCV 형식으로 변환
        try:
            pil_img = Image.open(img_path)
            img_array = np.array(pil_img)
            
            # RGB를 BGR로 변환 (OpenCV 형식)
            if len(img_array.shape) == 3:
                img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img = img_array
            print("PIL로 이미지 로드 성공")
        except Exception as e:
            print(f"PIL로도 이미지 로드 실패: {e}")
            
            # 방법 3: 한글 경로 문제 해결 (numpy를 이용한 방법)
            try:
                import numpy as np
                # 파일을 바이너리로 읽어서 디코드
                with open(img_path, 'rb') as f:
                    img_bytes = f.read()
                img_array = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                if img is not None:
                    print("바이너리 디코드로 이미지 로드 성공")
                else:
                    raise Exception("Binary decode failed")
            except Exception as e2:
                print(f"모든 방법으로 이미지 로드 실패: {e2}")
                return
    
    if img is None:
        print(f"이미지를 불러올 수 없습니다: {img_path}")
        print("다음을 확인해주세요:")
        print("1. 파일이 손상되지 않았는지")
        print("2. 지원되는 이미지 형식인지 (.jpg, .png, .bmp 등)")
        print("3. 파일 권한이 올바른지")
        return
    
    # OCR 실행
    result = reader.readtext(img_path)
    results = []
    
    print(f"검출된 텍스트 (신뢰도 {THRESHOLD}이상) :")
    print("-" * 50)
    
    for bbox, text, conf in result:
        if conf > THRESHOLD:
            print(f"텍스트: {text} (신뢰도: {conf:.2f})")
            results.append({'text': text, 'confidence': conf, 'bbox': bbox})
            
            # 바운딩 박스 좌표를 정수로 변환
            pt1 = tuple(map(int, bbox[0]))  # 좌상단
            pt2 = tuple(map(int, bbox[2]))  # 우하단
            
            # 네모박스 그리기 (초록색, 굵기 2)
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)
    
    print(f"\n총 {len(results)}개의 텍스트가 검출되었습니다.")
    
    # 결과 시각화
    plt.figure(figsize=(25, 25))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # BGR -> RGB 변환
    plt.axis('off')
    plt.title(f'OCR result (confidence {THRESHOLD} over)')
    plt.show()
    
    # 플롯 메모리 정리
    plt.close('all')
    
    return results

# 파일 존재 확인 및 실행
if __name__ == "__main__":
    import os
    
    # 현재 디렉토리의 이미지 파일들 확인
    print("현재 디렉토리의 이미지 파일들:")
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            print(f"  - {file}")
    
# 간단한 실행
if __name__ == "__main__":
    import os
    
    # 현재 디렉토리의 이미지 파일들 보여주기
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    image_files = [f for f in os.listdir('.') if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not image_files:
        print("이미지 파일을 찾을 수 없습니다!")
        img_path = input("이미지 파일 경로를 직접 입력하세요: ").strip()
        if os.path.exists(img_path):
            read(img_path)
        else:
            print("파일을 찾을 수 없습니다.")
    else:
        print("현재 디렉토리의 이미지 파일들:")
        for i, file in enumerate(image_files, 1):
            print(f"  {i}. {file}")
        
        try:
            # 숫자로 선택받기
            choice = input(f"\n처리할 파일 번호를 입력하세요 (1-{len(image_files)}): ").strip()
            file_index = int(choice) - 1
            
            if 0 <= file_index < len(image_files):
                selected_file = image_files[file_index]
                print(f"\n'{selected_file}' 처리중...")
                read(selected_file)
            else:
                print(f"잘못된 번호입니다. 1부터 {len(image_files)} 사이의 숫자를 입력해주세요.")
                
        except ValueError:
            print("숫자를 입력해주세요.")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")