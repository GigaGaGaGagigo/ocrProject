# cut_image DB에 저장을 위함(실제 연결되는지 확인 필요)

from db.crawl_sql import CutImage
from PIL import Image

def insert_cut_images(session, episode_id: int, paths: list):
    for idx, path in enumerate(paths):
        img = Image.open(path)
        height = img.height
        cut = CutImage(
            episode_id=episode_id,
            cut_number=idx + 1,
            image_path=path,
            height_px=height
        )
        session.add(cut)
    session.commit()
    print(f"[✅ cut_image 저장 완료] 총 {len(paths)}컷")