from typing import List

from fastapi import Depends, APIRouter, UploadFile, File, Security
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, bearer_scheme
from app.database import get_db
from app.dto.response.ReviewResponseSchemas import MyReviewResponse, ReviewPage
from app.services import profile_service

router = APIRouter()

@router.get("/profile/me",
            summary="프로필 정보 반환",
            description="이메일, 닉네임, 프로필 이미지 반환",
            dependencies=[Security(bearer_scheme)])
def my_profile(user= Depends(get_current_user)):
    return {"message": "인증 성공", "user": {
        "email": user["email"],
        "nickname": user["nick_name"],
        "profile_image": user.get("profile_image")
    }}

@router.patch("/profile/image",
              summary="프로필이미지 수정",
              description="이미지파일 포함해서 수정 요청 시 이미지링크 반환",
              dependencies=[Security(bearer_scheme)])
def update_profile_image(
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return profile_service.update_profile_image(db, user, image_file)


@router.get(
    "/profile/my-reviews",
    response_model=List[MyReviewResponse],
    summary="마이페이지 리뷰 최근 10개"
)
def my_recent_reviews(
        db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user),
        limit: int = 10
):
    return profile_service.my_recent_reviews(db, user_info, limit)


@router.get(
    "/profile/my-reviews/detail",
    response_model=ReviewPage,
    summary="마이페이지 리뷰 관리",
    description="리뷰 상세목록 페이지네이션 기반"
)
def my_review_management(
        db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user),
        page: int = Query(1, ge= 1),
        size: int = Query(3, ge= 1, le=50),
):
    return profile_service.my_review_management(db, user_info, page, size)
