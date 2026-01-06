from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite DB를 현재 폴더의 sql_app.db 파일로 연결
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"


# engine = DB 연결 객체
# connect_args={"check_same_thread": False}->
# SQLite는 기본적으로 한 쓰레드(쓰레드 = CPU가 일을 처리하는 최소 단위)에서만 연결 가능
# FastAPI 같은 비동기 환경에서 여러 쓰레드 사용 가능하게 하기 위해 False로 설정
# 쉽게 말해 여러 요청을 처리하기 위해 다음과 같이 구현
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal()을 호출하면 DB 세션 객체 생성
# autocommit=False로 설정하면 데이터를 변경했을때 commit 이라는 사인을 주어야만 실제 저장이 된다
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: ORM 모델 부모
Base = declarative_base()


# FastAPI에서 데이터베이스 연결을 안전하게 관리하기 위해 사용하는 의존성 주입(Dependency Injection)용 함수
# API 요청이 들어올 때마다 DB 연결을 생성하고, 작업이 끝나면 연결을 닫아주는 역할
# 의존성 주입:"어떤 객체가 사용하는 의존 객체를 직접 만들지 않고, 외부에서 넘겨주는 디자인 패턴
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
