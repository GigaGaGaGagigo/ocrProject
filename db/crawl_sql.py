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