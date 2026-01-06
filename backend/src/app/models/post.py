from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from app.database import Base
from sqlalchemy.orm import relationship


# 테이블의 구조를 정의
class Post(Base):
    # __tablename__은 모델에 의해 관리되는 테이블의 이름
    __tablename__ = "posts"

    id = Column(
        Integer, primary_key=True, index=True
    )  # primary_key=True->데이터가 생성 될 때마다 자동으로 1씩 증가

    title = Column(String)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 역할: 물리적으로 두 테이블을 연결합니다.
    # 외래키가 user table의 id를 참조
    # 실제 DB 컬럼: 데이터베이스의 posts 테이블에 author_id라는 숫자(Integer) 칸이 생깁니다.
    # ForeignKey("users.id"): "이 칸에 들어갈 숫자는 반드시 users 테이블의 id 값 중 하나여야 한다"는 제약 조건을 겁니다.
    # users는 테이블 네임
    author_id = Column(Integer, ForeignKey("users.id"))
    # 유저 객체와 매핑
    # 이 설정 덕분에 post.author_id라는 숫자 대신, **post.author**라고 치면 해당 글을 쓴 User 객체 전체에 바로 접근할 수 있습니다. (예: post.author.username)
    # back_populates="posts": 이는 '양방향' 연결을 의미합니다. User 모델 쪽에도 posts라는 이름의 관계가 설정되어 있어야 하며, 서로를 참조하게 됩니다.
    # 이 파일 내에서 알 수 있듯 테이블 네임이 posts
    author = relationship("User", back_populates="posts")
