from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 한국 표준시(KST: UTC+9) 함수 정의
def get_kst_now():
    return datetime.now(timezone(timedelta(hours=9)))

# SQLite 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./stockmaster.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 설문 결과 테이블 모델
class SurveyResult(Base):
    __tablename__ = "survey_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="guest_user")
    investor_type = Column(String(50))
    risk_score = Column(Integer)
    summary = Column(Text)
    advice = Column(Text)
    learning_roadmap = Column(Text)
    created_at = Column(DateTime, default=get_kst_now)  # 한국 시간으로 변경

# 테이블 생성 함수
def init_db():
    Base.metadata.create_all(bind=engine)

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()