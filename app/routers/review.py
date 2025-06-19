from typing import Union

from fastapi import APIRouter, Path, Depends, UploadFile, File, Security
from fastapi.params import Query
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db
from app.dto.response.ReviewResponseSchemas import ReviewScrollResponse, ReviewResponse, ReviewCreate
from app.services import review_service

router = APIRouter()
cookie_scheme = APIKeyCookie(name="access_token")

@router.get("/studio/{ps_id}/reviews",
            response_model=ReviewScrollResponse,
            summary="특정 매장에 대한 리뷰 상세 목록",
            description="""
                리뷰 상세 목록 API, ReviewScrollResponse Schema 참고 \n
                무한스크롤은 오프셋 활용
                초기값 offset = 0 -> 4 -> 8
                limit 값 더 해가며 호출하면 됨
                
                has_more가 끝지점인지 판단하는 변수
            """)
def get_reviews_by_studio(
        db: Session = Depends(get_db),
        ps_id: int = Path(..., description="매장 ID"),
        offset: int = Query(0, ge=0),
        limit: int = Query(4, ge=1, le=20),
):
    return review_service.get_review_details_in_photo_studio(db, ps_id, offset, limit)


@router.post("/reviews",
             response_model=ReviewResponse,
             summary="리뷰 등록 API (JWT 필수)",
             description="access_token 쿠키가 필수",
             dependencies=[Security(cookie_scheme)])
def post_review(
        db: Session = Depends(get_db),
        review: ReviewCreate = Depends(ReviewCreate.as_form),
        image: Union[UploadFile, None, str] = File(default=None), # 스웨거에서 send empty value 선택 시 image="" 로 보내어 422 에러 발생 방지 -> 이미지를 포함시키지 않음
        user_info: dict = Depends(get_current_user)
):
    user_id = int(user_info["sub"])
    return review_service.create_review(db, review, user_id, image_file=image)

