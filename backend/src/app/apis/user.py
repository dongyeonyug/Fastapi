from fastapi import APIRouter, Depends, HTTPException

from app.services.user_service import UserService, get_user_service
from schemas.user import UserCreate, UserResponse

router = APIRouter()

# 회원가입
# 반환형태인 UserResponse 스키마를 보면 해싱한 비밀번호(암호화된 비밀번호) 정보를 담고 있지 않으므로 반환값에 해당 정보는 포함되지 않는다.
# email: str
# username: str
# id: int
# created_at: datetime
# 다음과 같은 정보만 반환한다.
# 즉 정리하자면 create_user()함수를 통해 해싱한 비밀번호가 생성되더라도 그것이 클라이언트쪽으로 반환되지는 않는다.


@router.post(
    "/register",
    response_model=UserResponse,
    summary="회원가입",
    description="새로운 사용자를 등록합니다.",
    responses={
        409: {
            "description": "중복된 이메일로 회원가입 시도",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "이미 존재하는 이메일입니다.",
                    }
                }
            },
        }
    },
)
def register_user(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    # 이메일 , 사용자 이미 존재하면 회원가입 실패
    # 없을 경우 정상적으로 회원가입 실행
    existed_user_email = user_service.get_user_by_email(user.email)

    if existed_user_email:
        raise HTTPException(status_code=409, detail="이미 존재하는 이메일입니다.")

    existed_user_name = user_service.get_user_by_username(user.username)

    if existed_user_name:
        raise HTTPException(status_code=409, detail="이미 존재하는 사용자 이름입니다.")

    created_user = user_service.create_user(user)

    return created_user
