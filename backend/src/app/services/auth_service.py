from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.services.token_service import TokenService
from app.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token, verify_token
from app.utils.security import verify_password
from schemas.auth import LoginRequest
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends


# 사용자가 진짜 우리 회원인지 확인하고, 맞다면 jwt토큰 발급.
# 토큰 안에 user_id, email을 넣어두면, 나중에 서버가 이 토큰을 열었을 때 DB를 다시 조회하지 않고도 이 사람이 누구인지 즉시 알 수 있습니다.
# JWT(토큰)의 장점 ->서버가 가벼워짐: 세션 방식처럼 서버 메모리에 "누가 로그인했는지" 일일이 적어둘 필요가 없습니다. 서버는 그냥 토큰의 도장만 확인하면 됩니다.
# 확장성: 서버가 10대로 늘어나도, 똑같은 SECRET_KEY만 가지고 있다면 어떤 서버에서도 유저를 알아볼 수 있습니다.
# 이제 이 토큰을 받은 클라이언트(프론트엔드)는 보통 브라우저의 로컬 스토리지나 쿠키에 보관했다가, 다음 요청 때 Authorization: Bearer <토큰> 형식으로 서버에 보내게 됩니다.
class AuthService:
    def __init__(self, db: Session):
        self.db = db

    # 회원인증
    def authenticate_user(self, login_data: LoginRequest):
        query = select(User).where(User.email == login_data.email)

        user = self.db.execute(query).scalar_one_or_none()
        # DB조회 및 비밀번호 검증
        if not user or not verify_password(login_data.password, user.password):
            return None

        return user

    # 토큰생성
    def create_user_token(self, user: User):
        token_data = {
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        
        #refresh token
        refresh_token=create_refresh_token(
            data=token_data
                                           )

        TokenService.store_refresh_token(user.id,refresh_token)
        
        return {"access_token": access_token, "refresh_token":refresh_token, "token_type": "bearer"}
    
    def refresh_access_token(self, refresh_token:str):
        payload = verify_token(refresh_token)
        if not payload:
            return None
        
        user_id= payload.get("user_id")
        
        if not user_id:
            return None
        
        is_valid = TokenService.validate_refresh_token(user_id, refresh_token)
        if not is_valid:
            return None
        
        query=(
            select(User).
            where(User.id==user_id)
        )
        user=self.db.execute(query).scalar_one_or_none()
        
        if not user:
            return None
        
        token_data = {
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }
        
        access_token = create_access_token(token_data)
        
        
        return{
            "access_token":access_token,
            "token_type": " bearer"
        }

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)
