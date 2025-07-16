from typing import Optional, List

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.params import Query, Security
from sqlalchemy.orm import Session

from app.auth.jwt import bearer_scheme, get_current_user, get_optional_current_user
from app.database import get_db
from app.dto.response.StudioResponseSchemas import NearbyScrollResponse, RankedStudio, PhotoStudioDetail, \
    PhotoStudioGalleryPage
from app.models import User, PhotoStudio
from app.services import nearby_service, studio_service

router = APIRouter()

@router.get("/studios/nearby",
            summary= "주변 가까운 매장 조회(로그인 옵션)",
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
        category: Optional[str] = Query(None, description="필터할 카테고리 이름 (예: 복고)"),
        user_info: dict = Depends(get_optional_current_user),
):
    items, total, has_more = nearby_service.get_nearby_studios(
        db=db, lat=lat, lng=lng, offset=offset, limit=limit, category=category, user_info=user_info
    )
    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": has_more
    }


@router.get(
    "/studios/ranking",
    response_model=List[RankedStudio],
    summary="인기 매장 랭킹",
    description="""
        최근 '몇 일' 동안의 리뷰를 대상으로 가중평균 계산 \n
        이 API 호출할 때마다 이 데이터 기준으로 '#인기' 카테고리가 바뀜
    """
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
    summary="사진관 이미지 여러 개 업로드 (매장 이미지를 여러 개 업로드)",
    description="""
                여러 이미지 파일을 업로드하고 각 URL을 반환 \n
                
                test96@naver.com 아이디로 로그인해야 이미지 업로드 가능
                이외의 아이디는 권한 없음
                
                구축 계획 상 관리자 페이지가 없기 때문에 따로 API 호출할 곳을 만드셔야 합니다.
                """,
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
    description="""
                단일 이미지 파일을 업로드해서 사진관 썸네일을 등록/수정함 \n
                
                test96@naver.com 아이디로 로그인해야 이미지 업로드 가능
                이외의 아이디는 권한 없음
                
                구축 계획 상 관리자 페이지가 없기 때문에 따로 API 호출할 곳을 만드셔야 합니다.
                """,
    dependencies=[Security(bearer_scheme)]
)
def upload_studio_thumbnail(
        ps_id: int,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    return studio_service.add_studio_thumbnail(db, ps_id, file, user)

@router.get("/studios/{ps_id}",
            response_model=PhotoStudioDetail,
            summary="매장 상세",
            description="""
                매장 상세 페이지
            """)
def studio_detail(
        ps_id: int,
        db: Session = Depends(get_db)
):
    return studio_service.get_studio_detail(db, ps_id)

@router.get(
    "/studios/{ps_id}/images",
    response_model=PhotoStudioGalleryPage,
    summary="리뷰 사진 갤러리",
    description="""
        매장에 대한 리뷰 사진 갤러리
        page, size 파라미터로 9개씩 이미지를 반환 (사이즈 조정가능)
    """
)
def studio_gallery(
    ps_id: int,
    page: int = Query(1, ge=1, description="페이지 번호 1부터"),
    size: int = Query(9, ge=1, le=50, description="한 페이지당 이미지 수"),
    db: Session = Depends(get_db)
):
    images, has_more = studio_service.get_studio_gallery_page(db, ps_id, page, size)
    return PhotoStudioGalleryPage(
        page=page,
        size=size,
        has_more=has_more,
        images=images
    )