from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.models.post import Post
from app.models.user import User
from schemas.post import PostCreate, PostUpdate
from app.database import get_db


class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, post: PostCreate, user: User):
        # 사용자로부터 받은 데이터(Pydantic 모델)를 데이터베이스 테이블 형태(SQLAlchemy 모델)로 변환합니다.
        # 아직 DB는 이 객체의 존재를 모릅니다.
        created_post = Post(**post.model_dump())
        author_id = user.id
        # userid를 post테이블에 넣기
        created_post.author_id = author_id

        # DB에 담기
        # 생성한 객체를 SQLAlchemy의 작업 단위(Session)에 추가
        self.db.add(created_post)
        # DB에 확정(Commit) 하기
        self.db.commit()
        # DB에서 생성된 ID 등을 반영하기 위해 새로고침(Refresh)
        self.db.refresh(created_post)

        return created_post

    def get_posts(self):
        # SQL의 SELECT * FROM post와 같은 의미입니다. Post라는 DB 모델(테이블)에서 데이터를 가져오겠다는 선언
        query = select(Post).order_by(Post.created_at.desc())
        # 작성한 쿼리문을 DB에 실행
        posts = self.db.execute(query).scalars().all()

        return posts

    def get_post(self, post_id: int):
        query = select(Post).where(Post.id == post_id)
        post = self.db.execute(query).scalar_one_or_none()

        return post

    def update_post(self, post_id: int, post_update: PostUpdate, user: User):
        query = select(Post).where(Post.id == post_id)
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return None

        if post.author_id != user.id:
            raise HTTPException(status_code=403, detail="접근 권한 없습니다.")

        update_dict = {
            key: value
            for key, value in post_update.model_dump().items()
            if value is not None
        }

        for key, value in update_dict.items():
            setattr(post, key, value)

        self.db.commit()
        self.db.refresh(post)

        return post

    def delete_post(self, post_id: int, user: User):
        query = select(Post).where(Post.id == post_id)
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return False

        if post.author_id != user.id:
            raise HTTPException(status_code=403, detail="접근 권한 없습니다.")

        self.db.delete(post)
        self.db.commit()

        return True


def get_post_service(db: Session = Depends(get_db)):
    return PostService(db)
