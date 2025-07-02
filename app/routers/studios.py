from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.params import Query, Security
from sqlalchemy.orm import Session

from app.auth.jwt import bearer_scheme, get_current_user
from app.database import get_db
from app.dto.response.StudioResponseSchemas import NearbyScrollResponse, RankedStudio
from app.models import User
from app.services import nearby_service, studio_service

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


@router.get(
    "/studios/ranking",
    response_model=List[RankedStudio],
    summary="인기 매장 랭킹",
    description="최근 '몇 일' 동안의 리뷰를 대상으로 가중평균 계산"
)
def studio_ranking(
        db: Session = Depends(get_db),
        days: int = Query(7, ge=1, le=30),
        m: int = Query(5, ge=1, description="신뢰할 최소 리뷰 수"),
        limit: int = Query(10, ge=1, le=50)
):
    return studio_service.get_studio_ranking(db, days, m, limit)


@router.post(
    "/studios/{ps_id}/images",
    summary="사진관 이미지 여러 개 업로드",
    description="여러 이미지 파일을 업로드하고 각 URL을 반환",
    dependencies=[Security(bearer_scheme)]
)
def upload_studio_images(
        ps_id: int,
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    return studio_service.add_studio_images(db, ps_id, files, user)

@router.post(
    "/studios/{ps_id}/thumbnail",
    summary="사진관 썸네일 업로드/수정",
    description="단일 이미지 파일을 업로드해서 사진관 썸네일을 등록/수정함",
    dependencies=[Security(bearer_scheme)]
)
def upload_studio_thumbnail(
        ps_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    return studio_service.add_studio_thumbnail(db, ps_id, file, user)