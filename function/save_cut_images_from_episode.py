import requests
from PIL import Image
from io import BytesIO
from db.crawl_sql import CutImage  # cut_image 모델이 정의되어 있다고 가정
import os

def save_cut_images_from_episode(session, episode):
    base_url = episode.jpg_url.rsplit('_', 1)[0]  # '_IMAG01_1' → '_IMAG01'
    image_paths = []
    index = 1

    while True:
        image_url = f"{base_url}_{index}.jpg"
        response = requests.get(image_url)

        if response.status_code != 200:
            break  # 더 이상 이미지 없음

        # 이미지 저장 경로
        file_path = f"images/episode_{episode.id}_{index}.jpg"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 이미지 저장
        with open(file_path, 'wb') as f:
            f.write(response.content)

        # PIL로 높이 측정
        image = Image.open(BytesIO(response.content))
        image_height = image.height  # 단위: px

        # DB 저장
        cut_image = CutImage(
            episode_id=episode.id,
            image_path=file_path,
            image_height=image_height
        )
        session.add(cut_image)

        image_paths.append(file_path)
        index += 1

    session.commit()
    return image_paths