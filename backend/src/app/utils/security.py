from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호를 암호화해서 저장하기 위한 함수
# Type Hinting: password: str은 입력값이 문자열임을, -> str은 결과값도 문자열로 반환함을 명시
def get_password_hash(password: str) -> str:
    # 입력받은 평문 비밀번호(예: "mysecret123")를 bcrypt 알고리즘을 이용해 알아볼 수 없는 긴 문자열(해시)로 바꿉니다.
    return pwd_context.hash(password)


# 사용자가 로그인할 때 비밀번호가 맞는지 확인(검증)하기 위한 함수
def verify_password(plain_pasword: str, hashed_Password: str) -> bool:
    return pwd_context.verify(plain_pasword, hashed_Password)
