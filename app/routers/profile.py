from typing import List

from fastapi import Depends, APIRouter, UploadFile, File, Security, status
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, bearer_scheme
from app.database import get_db
from app.dto.request.ProfileRequestSchema import NicknameUpdateRequest, PasswordChangeRequest
from app.dto.response.ReviewResponseSchemas import MyReviewResponse, ReviewPage
from app.services import profile_service

router = APIRouter()

@router.get("/profile/me",
            summary="프로필 정보 반환",
            description="이메일, 닉네임, 프로필 이미지 반환",
            dependencies=[Security(bearer_scheme)])
def my_profile(db: Session = Depends(get_db), user= Depends(get_current_user)):
    return profile_service.get_current_profile_me(db, user)

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


@router.delete(
    "/profile/reviews/{review_id}",
    summary="리뷰 삭제 (본인만)",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_my_review(
        review_id: int,
        db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user)
):
    return profile_service.delete_my_review(review_id, db, user_info)


@router.patch("/profile/me/nickname",
              summary="닉네임 변경",
              description="""
                최소 2자 ~ 최대 10자, 한글 기준 \n
                닉네임 중복 불가, 중복 시 409 Conflict 에러코드 반환
              """,
              dependencies=[Security(bearer_scheme)])
def update_nickname(
        payload: NicknameUpdateRequest,
        db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user),
):
    return profile_service.update_profile_nickname(payload, db, user_info)

@router.post("/profile/me/password/verify",
             summary="현재 비밀번호 확인",
             description="""
                현재 비밀번호 변경 \n
                성공 시 서버 내에서 5분 동안 시간 체크함
                시간 초과 시 비밀번호 변경 API 사용 불가, 재확인 필요
             """)
def verify_current_password(
    current_password: str,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user)
):
    return profile_service.verify_current_password(current_password, db, user_info)

@router.patch("/profile/me/password",
              summary="새 비밀번호 변경",
              description="""
              새 비밀번호 변경 \n
              우선
              1. 현재 비밀번호 확인 API 정상응답이 반드시 필요함
              2. 1번 성공 시 이 API를 사용하기 위한 5분이 주어짐, 지나면 401에러
              """)
def change_password(
        payload: PasswordChangeRequest,
        db: Session = Depends(get_db),
        user_info: dict = Depends(get_current_user)
):
    return profile_service.change_password(payload, db, user_info)