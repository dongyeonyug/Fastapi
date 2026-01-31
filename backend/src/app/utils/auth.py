from datetime import datetime, time, timedelta
from typing import Optional
from jose import jwt, JWTError

SECRET_KEY = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 쉽게 비유하자면, **인코딩은 '암호화해서 편지 봉투에 담는 것'**이고, **디코딩은 '봉투를 뜯어서 내용을 해석하는 것
# 인코딩: 데이터를 특정 형식(포맷)으로 변환하는 과정  예시 (JWT):사용자 정보({"id": "user123"})를 jwt.encode를 통해 eyJhbGciOiJIUzI1... 같은 복잡한 문자열로 만드는 것,
# 디코딩 :인코딩된 데이터를 다시 원래의 상태로 되돌리는 과정입니다.  예시 (JWT):클라이언트가 보낸 복잡한 토큰 문자열을 서버가 비밀키로 풀어서 "아, 이 사람은 user123이구나!"라고 알아내는 것이 jwt.decode입니다.


# access토큰을 생성하는 유틸함수
# optional-> 값이 있을 수도 있고 없을 수도 있다.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # 사용자가 특정 시간(예: "난 1시간 유지할래")을 넘겨줬다면(expires_delta): 현재 시각 + 그 시간만큼을 만료 시간으로 잡습니다.
    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    # 아무것도 안 넘겨줬다면(None): 미리 정해둔 기본값인 30분 뒤를 만료 시간으로 잡습니다.
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 복사한 데이터에 exp(만료일)라는 약속된 키를 집어넣습니다.
    to_encode.update({"exp": expire})

    # jwt.encode 함수가 데이터 + 비밀키 + 알고리즘을 섞어서 암호화된 긴 문자열을 만들어냅니다.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#refresh token의 경우 유저를 인식할 수 있는 최소한의 정보만 보통 담는다.
#access token보다 만료기간이 긴 경우가 대부분이다.
def create_refresh_token(data:dict)->str:
    
    user_id=data["user_id"]
    
    expire =datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_payload={
        "user_id": user_id,
        "exp":expire,
        "type":"refresh"
    }
    
    encoded_jwt=jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

"""
JWT 토큰의 남은 만료 시간을 초 단위로 계산
"""
def get_token_expiry(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        
        if exp:
            # 현재 시간과 만료 시간의 차이 계산
            remaining = exp - time.time()
            # 최소 1초 이상 설정
            return max(int(remaining), 1)
    except:  # noqa: E722
        pass
    
    # 기본값 (30분)
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60