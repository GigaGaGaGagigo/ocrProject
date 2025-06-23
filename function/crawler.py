from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def capture_webtoon_image(url, save_path="webtoon_capture.png"):
    options = Options()
    options.add_argument('--headless')  # 브라우저 없이 실행
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1080,3000')  # 충분히 긴 화면

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)  # 로딩 대기

    driver.save_screenshot(save_path)
    driver.quit()

    return save_path