from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.utils.security import get_password_hash
from schemas.user import UserCreate
from app.database import get_db
from fastapi import Depends


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email, username=user.username, password=hashed_password
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)

        return self.db.execute(query).scalar_one_or_none()

    def get_user_by_username(self, username: str):
        query = select(User).where(User.username == username)

        return self.db.execute(query).scalar_one_or_none()


def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)
