from sqlalchemy import Column, Integer, String, Text
from db.database import Base

class Webtoon(Base):
    __tablename__ = 'webtoon'

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer)
    title = Column(String(255))
    company = Column(String(100))
    language = Column(String(10))  # ex: 'kr', 'en'
    genre = Column(Integer)        # 0=로맨스, 1=액션, ...
    url = Column(Text)

class WebtoonGroup(Base):
    __tablename__ = "webtoon_group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(255))

class Episode(Base):
    __tablename__ = 'episode'

    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer)
    episode_number = Column(Integer)
    lang = Column(String(10))     # 'kr', 'en'
    url = Column(Text)            # 에피소드 웹 URL
    jpg_url = Column(Text)        # 이미지 시드 URL, 예: https://.../_IMAG01_1.jpg
    cut_size = Column(Integer, default=0)

class CutImage(Base):
    __tablename__ = 'cut_image'

    id = Column(Integer, primary_key=True, index=True)
    webtoon_id = Column(Integer)
    episode_id = Column(Integer)
    cut_number = Column(Integer)
    image_path = Column(String(500))
    height_px = Column(Integer)  # px 단위, 추후 계산해서 넣을 수 있음