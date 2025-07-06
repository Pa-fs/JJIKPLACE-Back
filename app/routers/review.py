from typing import Union

from fastapi import APIRouter, Path, Depends, UploadFile, File, Security, Request, Response
from fastapi.params import Query
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, bearer_scheme
from app.database import get_db
from app.dto.response.ReviewResponseSchemas import ReviewScrollResponse, ReviewResponse, ReviewCreate, ReviewDetail
from app.services import review_service

router = APIRouter()
cookie_scheme = APIKeyCookie(name="access_token")

@router.get("/studios/{ps_id}/reviews",
            response_model=ReviewScrollResponse,
            summary="특정 매장에 대한 리뷰 상세 목록",
            description="""
                리뷰 상세 목록 API, ReviewScrollResponse Schema 참고 \n
                무한스크롤은 오프셋 활용
                초기값 offset = 0 -> 4 -> 8
                limit 값 더 해가며 호출하면 됨
                
                has_more가 끝지점인지 판단하는 변수
                
                # ETag 추가 (캐시 활용), 변경 없으면 304 Not Modified 반환, 있으면 새로운 값 응답
                서버 응답
                ETag: "26f99042bc7930933af17f90f0ec150a277d7a37a29441793a93108e3f05a402"
                Last-Modified: Thu, 26 Jun 2025 17:57:10 GMT (최신리뷰 기준 날짜)
                
                클라이언트 -> 서버 요청 시
                If-None-Match: <Etag값>
                If-Modified-Since: <Last-Modified 날짜값>
            """)
def get_reviews_by_studio(
        request: Request, # 클라이언트 헤더 읽기용
        response: Response, # 응답 헤더 세팅용
        db: Session = Depends(get_db),
        ps_id: int = Path(..., description="매장 ID"),
        offset: int = Query(0, ge=0),
        limit: int = Query(4, ge=1, le=20),
):
    return review_service.get_review_details_in_photo_studio(db, ps_id, offset, limit, request, response)


@router.post("/review",
             response_model=ReviewResponse,
             summary="리뷰 등록",
             description="""
                         access_token 쿠키가 필수 \n
                         허용 확장자: .jpg, .jpeg, .png, .gif, .webp
                         허용 용량: 5 MB \n
                         """,
             dependencies=[Security(bearer_scheme)])
def post_review(
        db: Session = Depends(get_db),
        review: ReviewCreate = Depends(ReviewCreate.as_form),
        image: Union[UploadFile, None, str] = File(default=None, description="리뷰 이미지 (선택)"), # 스웨거에서 send empty value 선택 시 image="" 로 보내어 422 에러 발생 방지 -> 이미지를 포함시키지 않음
        user_info: dict = Depends(get_current_user)
):
    user_email = user_info["email"]
    return review_service.create_review(db, review, user_email, image_file=image)


@router.get(
    "/studios/{ps_id}/reviews/{review_id}",
    response_model=ReviewDetail,
    summary="리뷰 상세 조회 (단 건)"
)
def a_detail_review(
        db: Session = Depends(get_db),
        ps_id: int = Path(..., description="매장 ID"),
        review_id: int = Path(..., description="리뷰 ID"),
):
    return review_service.a_review_detail(db, ps_id, review_id)
