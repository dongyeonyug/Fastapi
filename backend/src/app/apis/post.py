from typing import List
from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.post_service import PostService, get_post_service
from schemas.post import PostCreate, PostResponse, PostUpdate



from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os


router = APIRouter()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@router.get("/create", response_class=HTMLResponse)
async def get_posts_view_page(request: Request):
    # templates 디렉토리 안의 login.html을 읽어서 반환합니다.
    return templates.TemplateResponse("posts_create.html", {"request": request})



# 게시글 생성
# pydantic :외부에서 들어온 데이터가 "내가 원하는 모양과 타입이 맞는지" 확인하고, 맞다면 "파이썬 객체로 변환"해주는 필터 역할
# current_user: User = Depends(get_current_user) - 로그인 요구 될 포인트마다 의존성 함수 주입
@router.post(
    "/create",
    response_model=PostResponse,
    summary="새 게시글",
    description="새로운 게시글을 생성합니다.",
)
def create_post(
    post: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    created_post = post_service.create_post(post, current_user)

    return created_post


#전체 게시글 목록 화면에 출력.
# 1. HTML 화면을 보여주는 경로 (브라우저 접속용: http://localhost:8000/posts_view)
#동작원리 함수동작시 posts_view.html실행-> html파일 내에서 get으로 posts 불러옴.
@router.get("/posts/view", response_class=HTMLResponse)
async def get_PostsView_page(request: Request):
    # templates 디렉토리 안의 login.html을 읽어서 반환합니다.
    return templates.TemplateResponse("posts_view.html", {"request": request})



# 전체 게시글 목록 조회
@router.get(
    "/posts/",
    response_model=List[PostResponse],
    summary="게시글 목록 조회",
    description="전체 게시글 목록을 조회합니다.",
    responses={
        404: {
            "description": "게시글 조회 실패",
            "content": {
                "application/json": {
                    "example": {"detail": "게시글을 찾을 수 없습니다."}
                }
            },
        },
        400: {
            "description": "게시글 조회 실패",
            "content": {
                "application/json": {
                    "example": {"detail": "전송 데이터가 잘못됐습니다."}
                }
            },
        },
    },
)
def get_posts(post_service: PostService = Depends(get_post_service)):
    posts = post_service.get_posts()

    if posts is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return posts


# 특정 게시글 조회
# 타입힌트 -> 문법: name: str (name은 문자열이어야 해)
@router.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="특정 게시글 조회",
    description="게시글 ID를 기반으로 특정 게시글을 조회합니다.",
    responses={
        404: {
            "description": "게시글 조회 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글을 찾을 수 없습니다.",
                    }
                }
            },
        }
    },
)
def get_post(post_id: int, post_service: PostService = Depends(get_post_service)):
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return post


# 게시글 수정
@router.patch(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="게시글 수정",
    description="게시글을 수정합니다.",
    responses={
        404: {
            "description": "게시글 수정 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글을 찾을 수 없습니다.",
                    }
                }
            },
        }
    },
)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    post = post_service.update_post(post_id, post_update, current_user)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return post


# 게시글 삭제
@router.delete(
    "/posts/{post_id}",
    response_model=dict,
    summary="게시글 삭제",
    description="게시글을 삭제합니다.",
    responses={
        200: {
            "description": "게시글 삭제 성공",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글이 성공적으로 삭제되었습니다.",
                    }
                }
            },
        },
        404: {
            "description": "게시글 삭제 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "게시글을 찾을 수 없습니다.",
                    }
                }
            },
        },
    },
)
def delete_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user),
):
    post = post_service.delete_post(post_id, current_user)

    if post is False:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return {"message ": "성공적으로 게시글이 삭제되었습니다."}
