from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DB 연결 정보
DB_USER = 'root'
DB_PASSWORD = 'mysql비밀번호입력'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ocrproject'

# SQLAlchemy용 URL 구성
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base 클래스 (모델들이 상속할 베이스)
Base = declarative_base()
