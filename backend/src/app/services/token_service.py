from datetime import time, timedelta
from app.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY
from app.core.redis_config import redis_client
from jose import jwt

# Redis 내의 다른 데이터와 섞이지 않도록 식별자(Prefix)를 붙입니다. (예: blacklist:abcd123...)
TOKEN_BLACKLIST_PREFIX = "blacklist"
# 블랙리스트에 등록할 기간입니다. 기본값은 30분($60 \times 30$초)으로 설정되어 있습니다
DEFAULT_TOKEN_EXPIRY = 60 * 30

REFRESH_TOKEN_PREFIX="refresh:"

# Redis를 활용한 JWT(또는 Access Token) 블랙리스트 관리 서비스입니다. 보통 사용자가 로그아웃을 하거나, 특정 토큰을 강제로 무효화해야 할 때 보안상의 이유로 사용


class TokenService:
    # blacklist_token 메서드 (토큰 무효화) 사용자가 로그아웃을 요청하면 해당 토큰을 Redis에 저장하여 "사용 불가" 상태로 만듭니다.
    #이 메서드는 개별 '객체(인스턴스)'가 아니라, '클래스 그 자체'에 속하는 메서드야"라고 선언하는 것입니다.
    @classmethod
    def blacklist_token(cls, token: str, expires_in: int = DEFAULT_TOKEN_EXPIRY):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        # Redis에 'key: "1"' 형태의 데이터를 저장하고 유효기간(ex) 설정
        # 작동 원리: Redis의 SET 명령어를 사용합니다. ex 옵션을 주어 특정 시간이 지나면 Redis에서 자동으로 삭제되게 합니다.
        redis_client.set(key, "1", ex=expires_in)
        return True

    # API 요청이 들어올 때마다 해당 토큰이 블랙리스트에 있는지 확인합니다.
    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        # 해당 키가 Redis에 존재하는지 확인 (있으면 1, 없으면 0 반환)
        # 작동 원리: EXISTS 명령어를 통해 해당 토큰이 블랙리스트에 등록되어 있는지 체크합니다. 만약 결과가 True라면 서버는 해당 요청을 거부(Unauthorized)해야 합니다.
        return redis_client.exists(key) == 1
    
    @classmethod
    def store_refresh_token(cls, user_id:int, refresh_token: str):
        
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        
        with redis_client.pipeline() as pipe:
            
            #해당 유저의 키(user_key)라는 주머니(Set)에 refresh_token을 집어넣습니다.  한 유저가 여러 기기에서 로그인할 수 있으니 집합 구조를 씁니다.
            pipe.sadd(user_key,refresh_token)
            
            #만료 시간 설정 (expire)
            #이 데이터는 며칠 뒤에 자동으로 삭제해라"**라고 유효기간을 초 단위로 설정하는 것입니다.
            expire_seconds=int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS+1).total_seconds())
            pipe.expire(user_key,expire_seconds)
            
            #바구니에 담긴 모든 명령(sadd, expire)을 Redis 서버로 실제로 전송
            pipe.execute()

        return True
    
    #저장했던 Refresh Token이 "진짜인지, 그리고 아직 유효한지"를 확인하는 검증(Validation) 로직
    @classmethod
    def validate_refresh_token(cls, user_id:int, refresh_token: str)->bool:
        
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"

        # sismember: "Set Is Member"의 약자입니다.
        # 역할: user_key라는 이름의 주머니(Set) 안에 refresh_token이라는 값이 존재하는지 확인합니다.
        # 결과값:
        # 주머니 안에 토큰이 있으면? True (인증 성공!)
        # 없으면(만료되었거나, 로그아웃했거나, 가짜 토큰이면)? False (인증 실패!)
        return redis_client.sismember(user_key, refresh_token)
    
    #모든 refresh 토큰 무효화
    @classmethod
    def revoke_refresh_token(cls, user_id:int, refresh_token: str=None):
        
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"

        if refresh_token:
            redis_client.srem(user_key,refresh_token)
        else:
            redis_client.delete(user_key)
        return True
    

    
