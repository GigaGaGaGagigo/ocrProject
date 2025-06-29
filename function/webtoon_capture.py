# 이미지 캡쳐 함수 (오류 확인 필요)
# Selenium 캡처용

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import time

def capture_webtoon_image(url, base_name="webtoon_capture", chunk_height=3000, chunk_limit=30):
    options = Options()
    options.add_argument('--headless')
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
        time.sleep(2)

        png = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(png)).crop((0, 0, 1500, 3000))
        chunks.append(image)

        scroll_pos += viewport_height
        index += 1

        if driver.execute_script("return window.pageYOffset + window.innerHeight") >= total_height:
            break

    driver.quit()

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

    return saved_paths