from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.token_service import TokenService
from app.utils.auth import verify_token
from sqlalchemy import select

# HTTPBearer(): FastAPI에서 제공하는 보안 클래스입니다. 클라이언트가 HTTP 헤더에 Authorization: Bearer <토큰> 형식으로 데이터를 보냈는지 자동으로 확인
# 역할: 클라이언트가 보낸 HTTP 헤더에서 Authorization: Bearer <토큰> 형태의 데이터를 찾아내는 규격을 정의합니다.
# FastAPI의 Swagger UI(/docs) 우측 상단에 'Authorize' 버튼을 생성해주는 역할도 합니다.
bearer_scheme = HTTPBearer()


# JWT(JSON Web Token) 등을 활용해 현재 로그인한 "사용자를 식별"하는 '의존성 주입(Dependency Injection)' 함수
# 토큰 추출: credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme) 부분에서 헤더에 담긴 Bearer 토큰을 가져옵니다.
def get_current_user(
    # 브라우저나 앱이 보낸 헤더에서 토큰 값만 쏙 뽑아옵니다.
    # 만약 헤더에 토큰이 없으면, 이 시점에서 이미 403 Forbidden 에러를 반환하며 함수 실행을 중단합니다.
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    #추출된 HTTPAuthorizationCredentials 객체에서 실제 문자열 형태의 토큰(예: eyJhbG...)만 변수에 담습니다.
    token = credentials.credentials
    
    #만약 블랙리스트에 포함된 토큰이라면  HTTPException 처리
    if TokenService.is_token_blacklisted(token):
        raise HTTPException(
            status_code=401,
            detail="만료된 토큰입니다.",
            headers={'WWW-Authenticate': "Bearer"}
        )
        
    
    
    # 토큰 검증: verify_token(token)을 실행하여 토큰이 진짜인지 확인합니다.
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 사용자 정보 추출: 토큰 안에 들어있는 username을 꺼냅니다.
    username = payload.get("username")

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # DB 실재 확인: 추출한 username으로 실제 데이터베이스에서 사용자 정보를 조회합니다.
    query = select(User).where(User.username == username)
    # DB 실재 확인: 추출한 username으로 실제 데이터베이스에서 사용자 정보를 조회합니다.
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
