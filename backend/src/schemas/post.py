# 스키마란 쉽게 말해 "데이터가 어떻게 생겨야 하는지 정의한 설계도

from datetime import datetime
from pydantic import BaseModel


# 사용자가 새로운 게시글을 작성할 때 서버로 보내야 하는 데이터의 형식
class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


# 서버가 처리를 마치고 사용자(클라이언트)에게 응답할 때의 형식
class PostResponse(BaseModel):
    id: int
    author_id: int
    title: str
    content: str
    created_at: datetime

    # 이 설정은 Pydantic 모델이 데이터베이스 객체(ORM 모델)를 읽을 수 있게 해주는 스위치입니다.
    # 기본적으로 Pydantic은 dict 형태의 데이터만 읽을 수 있습니다.
    # 하지만 실제 개발 시에는 SQLAlchemy 같은 DB 모델을 결과값으로 받게 되는데, 이 설정이 있어야 post.title 같은 객체 속성 접근 방식을 이해하고 자동으로 JSON 데이터로 변환해 줍니다. (Pydantic V1에서는 orm_mode = True라고 썼던 설정입니다.)
    class Config:
        from_attributes = True
