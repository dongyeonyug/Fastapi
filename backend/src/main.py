
from fastapi import FastAPI,Request
from app.apis import auth, post, user
from app.core.redis_config import init_redis
from app.database import engine, Base

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 정적 파일(CSS/JS) 사용 시 필요


app = FastAPI(
    title="FastApi Ncp Mailing Service",
    description="게시판과 Ncp 메일 발송 기능을 제공하는 서비스입니다.",
    version="1.0.0",
    docs_url="/docs",
    redot_url="/redoc",
)





# app.apis.user
app.include_router(user.router, tags=["user"])

# app.apis.post
app.include_router(post.router, prefix="/posts", tags=["post"])

# app.apis.auth
app.include_router(auth.router, tags=["auth"])

# Redis 초기화
init_redis(app)


@app.get("/")
def health_check():
    return {"status": "ok"}


# sqlite와 제대로 연결되었는지 확인
@app.get("/ping")
async def ping_db():
    try:
        with engine.connect() as conn:
            return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 설계한 DB테이블을 실제로 DB에생성
# Base.metadata: 앞서 models.py에서 class Post(Base)처럼 Base를 상속받아 만들었던 모든 모델(설계도)의 정보를 수집해 놓은 보관함입니다.
# create_all: "보관함에 담긴 모든 설계도를 바탕으로 DB에 테이블을 만들어라"라는 명령입니다.
# bind=engine: "어떤 DB에 만들까?"에 대한 답입니다. engine에는 SQLite나 PostgreSQL 같은 실제 DB 연결 정보가 담겨 있습니다.
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)
