
from fastapi import APIRouter, Depends, HTTPException,Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import AuthService, get_auth_service

from app.services.token_service import TokenService
from app.utils.auth import get_token_expiry
from schemas.auth import LoginRequest, TokenResponse



from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os


router = APIRouter()
#bearer_scheme = HTTPBearer()는 FastAPI에서 "이 서비스는 HTTP Bearer 방식의 인증을 사용한다"라고 선언하는 일종의 약속(Security Scheme)입니다.
#1. HTTP Bearer 방식이란? 'Bearer'는 사전적으로 '소지자, 운반자'라는 뜻입니다. 즉, **"이 토큰을 가지고 있는(소지한) 사람을 주인으로 인정해줘"**라는 방식의 인증 제도입니다.
#보통 클라이언트가 서버에 요청을 보낼 때, HTTP 헤더에 다음과 같은 형식으로 토큰을 실어 보냅니다:Authorization: Bearer eyJhbGciOiJIUzI1...
#앞서 질문하신 [Authorize] 버튼이 생기는 이유가 바로 이것입니다. 이 코드를 작성하는 순간, FastAPI는 OpenAPI 표준에 맞춰 "이 API는 Bearer 인증이 필요함"이라는 정보를 생성하고, 이를 바탕으로 스웨거 페이지에 자물쇠 아이콘과 토큰 입력창을 만들어줍니다.
bearer_scheme = HTTPBearer()

# 회원가입
# 반환형태인 UserResponse 스키마를 보면 해싱한 비밀번호(암호화된 비밀번호) 정보를 담고 있지 않으므로 반환값에 해당 정보는 포함되지 않는다.
# email: str
# username: str
# id: int
# created_at: datetime
# 다음과 같은 정보만 반환한다.
# 즉 정리하자면 create_user()함수를 통해 해싱한 비밀번호가 생성되더라도 그것이 클라이언트쪽으로 반환되지는 않는다.



# 현재 파일(auth.py)의 위치를 기준으로 프로젝트 루트(src) 경로를 계산합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

#response_class=HTMLResponse->서버가 브라우저에게 보내는 결과물의 형식을 HTML로 지정
#request: Request->클라이언트(브라우저)가 서버에 보낸 모든 정보가 담긴 가방이라고 생각하시면 됩니다. 기능: 접속한 사람의 IP 주소, 쿠키, 헤더 정보, 브라우저 종류 등의 데이터를 담고 있습니다.

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    # templates 디렉토리 안의 login.html을 읽어서 반환합니다.
    return templates.TemplateResponse("login.html", {"request": request})




@router.post(
    "/login",
    response_model=TokenResponse,
    summary="로그인",
    description="사용자 로그인 후 JWT토큰을 발급합니다.",
    responses={
        401: {
            "description": "인증실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "인증실패",
                    }
                }
            },
        }
    },
)
def login(
    login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    
    # 전송받은 데이터 확인용 (터미널에 출력됨)
    print(f"로그인 시도 이메일: {login_data.email}")
    print(f"로그인 시도 비밀번호: {login_data.password}")
    
    user = auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=401, detail="인증실패", headers={"WWW-Authenticate": "Bearer"}
        )

    token_data = auth_service.create_user_token(user)
    print(token_data)
    return token_data

@router.post(
        "/logout",
        summary="사용자 로그아웃",
        description="사용자 로그아웃",
        responses={
            200: {
                "description": "로그아웃 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "로그아웃되었습니다.",
                        }
                    }
                }
            }
        }
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    ):
    # 헤더에서 토큰 추출
    token = credentials.credentials

    # 현재 토큰의 만료 시간 계산
    token_expiry = get_token_expiry(token)
    
    # 토큰을 블랙리스트에 추가
    TokenService.blacklist_token(token, token_expiry)
    
    return {"message": "로그아웃되었습니다."}