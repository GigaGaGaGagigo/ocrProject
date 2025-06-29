import cv2
from PIL import Image
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


def load_image_as_array(img_path="", gray=False):
    img_path = str(img_path)

    if not gray:
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2RGB)
    else:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    return img


def save_image(img, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if img.ndim == 3:
        cv2.imwrite(filename=str(path), img=img[:, :, :: -1], params=[cv2.IMWRITE_JPEG_QUALITY, 100])
    elif img.ndim == 2:
        cv2.imwrite(filename=str(path), img=img, params=[cv2.IMWRITE_JPEG_QUALITY, 100])


def show_image(img1, img2=None, alpha=0.5):
    plt.figure(figsize=(11, 9))
    plt.imshow(img1)
    if img2 is not None:
        plt.imshow(img2, alpha=alpha)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def convert_to_pil(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return img


def convert_to_array(img):
    img = np.array(img)
    return img


def draw_easyocr_result(img, bboxes):
    img_copied = convert_to_pil(img.copy())
    draw = ImageDraw.Draw(img_copied)

    for bbox_points, text, confidence in bboxes:
        x_coords = [point[0] for point in bbox_points]
        y_coords = [point[1] for point in bbox_points]
        
        xmin = int(min(x_coords))
        ymin = int(min(y_coords))
        xmax = int(max(x_coords))
        ymax = int(max(y_coords))

        # 바운딩 박스 그리기
        draw.rectangle(xy=(xmin, ymin, xmax, ymax), outline=(255, 0, 0), width=2)

        # 텍스트 + 신뢰도 조합
        label = f"{text} ({confidence:.2f})"

        # 폰트 설정
        try:
            font = ImageFont.truetype("fonts/NanumSquareNeo-bRg.ttf", size=22)
        except:
            font = ImageFont.load_default()

        # 텍스트 표시
        draw.text(
            xy=(xmin, ymin - 4),
            text=label,
            fill=(255, 0, 0),
            font=font,
            anchor="ls"
        )

    return img_copied


def get_image_cropped_by_rectangle(img, xmin, ymin, xmax, ymax):
    if img.ndim == 3:
        return img[ymin: ymax, xmin: xmax, :]
    else:
        return img[ymin: ymax, xmin: xmax]
