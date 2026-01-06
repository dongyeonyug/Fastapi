import redis
from fastapi import FastAPI

# Redis 연결 설정
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

# Redis 클라이언트
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True  # 문자열 응답을 자동으로 디코딩
)

def init_redis(app: FastAPI):
    """
    FastAPI 앱에 Redis 클라이언트 연결
    """
    @app.on_event("startup")
    async def startup_redis_client():
        try:
            # Redis 연결 테스트
            redis_client.ping()
            print("Redis connection established")
        except redis.exceptions.ConnectionError:
            print("Failed to connect to Redis")
    
    @app.on_event("shutdown")
    async def shutdown_redis_client():
        redis_client.close()
        print("Redis connection closed")