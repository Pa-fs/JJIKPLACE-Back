from fastapi import APIRouter, Path, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dto.response.ReviewResponseSchemas import ReviewScrollResponse
from app.services import review_service

router = APIRouter()

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
