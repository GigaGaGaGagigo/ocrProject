from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DB 연결 정보
DB_USER = 'your_user'         # 본인 DB 계정
DB_PASSWORD = 'your_password' # 본인 DB 비밀번호
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'your_db_name'      # 실제 사용할 DB 이름


# SQLAlchemy용 URL 구성
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base 클래스 (모델들이 상속할 베이스)
Base = declarative_base()