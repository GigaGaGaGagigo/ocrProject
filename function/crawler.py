from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
import io
import os

def capture_webtoon_image(url, base_name="webtoon_capture", chunk_height=3000, chunk_limit=30):
    options = Options()
    options.add_argument('--headless')  # 창 없이 실행
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1500,3000')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = chunk_height
    chunks = []

    scroll_pos = 0
    index = 0

    while scroll_pos < total_height:
        driver.execute_script(f"window.scrollTo(0, {scroll_pos})")
        time.sleep(2)  # 로딩 대기

        png = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(png)).crop((0, 0, 1500, 3000))
        chunks.append(image)

        scroll_pos += viewport_height
        index += 1

        # 스크롤이 끝났으면 중단
        if driver.execute_script("return window.pageYOffset + window.innerHeight") >= total_height:
            break

    driver.quit()

    # 이미지 이어붙이기 및 다중 저장
    total_groups = (len(chunks) + chunk_limit - 1) // chunk_limit
    saved_paths = []

    for group_index in range(total_groups):
        group_chunks = chunks[group_index * chunk_limit : (group_index + 1) * chunk_limit]
        group_height = len(group_chunks) * chunk_height

        stitched = Image.new('RGB', (1500, group_height))
        for i, img in enumerate(group_chunks):
            stitched.paste(img, (0, i * chunk_height))

        save_path = f"{base_name}_{group_index + 1}.png"
        stitched.save(save_path)
        saved_paths.append(save_path)

    return saved_paths  # 여러 개의 저장된 경로 리스트 반환

def jpg_url_update(url: str, num: int) -> str:
    # 1. 마지막 5글자 제거 (예: '1.jpg')
    url = url[:-5]

    # 2. 뒤에서부터 '_'가 나올 때까지 한 글자씩 제거
    while url and url[-1] != '_':
        url = url[:-1]

    # 3. `_`가 포함되어 있다면 num을 붙이고 `.jpg` 확장자 추가
    if url.endswith('_'):
        return f"{url}{num}.jpg"
    else:
        raise ValueError("유효한 base URL 형식이 아닙니다.")