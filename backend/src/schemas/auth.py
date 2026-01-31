from datetime import datetime
from pydantic import BaseModel, Field

# class LoginRequest(BaseModel): 이 클래스는 "앞으로 들어올 데이터는 반드시 email과 password라는 키를 가진 JSON이어야 한다"라고 선언하는 것입니다.
# JSON → Pydantic 변환: FastAPI의 login 함수에서 login_data: LoginRequest라고 타입을 지정하는 순간, FastAPI는 이 BaseModel을 상속받은 LoginRequest 클래스를 사용하여 들어오는 JSON의 유효성을 검사하고 객체로 만듭니다.
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token:str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str
    
