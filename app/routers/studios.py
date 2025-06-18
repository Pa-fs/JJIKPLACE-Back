from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dto.response.StudioResponseSchemas import NearbyScrollResponse
from app.services import nearby_service

router = APIRouter()

@router.get("/studios/nearby",
            summary= "주변 가까운 매장 조회",
            response_model=NearbyScrollResponse,
            description="""
                주변 가까운 매장 조회 API (기본 5km 이내), NearbyScrollResponse Schema 참고 \n
                무한스크롤은 오프셋 활용
                초기값 offset = 0 -> 4 -> 8
                limit 값 더 해가며 호출하면 됨

                has_more가 끝지점인지 판단하는 변수
            """)
def get_nearby_studios(
        db: Session = Depends(get_db),
        lat: float = Query(35.86788218095435, description="선택된 마커의 위도"),
        lng: float = Query(128.59860663344742, description="선택된 마커의 경도"),
        offset: int = Query(0, ge=0, le=1000, description="스크롤 당 시작 위치"),
        limit: int = Query(3, ge=3, le=1000, description="스크롤 당 항목 요청 개수"),
        category: Optional[str] = Query(None, description="필터할 카테고리 이름 (예: 복고)")
):
    items, total = nearby_service.get_nearby_studios(db, lat, lng, offset, limit, category)
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + len(items) < total
    }