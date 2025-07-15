from typing import List

from pydantic import BaseModel, Field
from typing_extensions import Optional


class NearbyStudioItem(BaseModel):
    ps_id: int = Field(..., description="매장 식별 ID")
    name: str = Field(..., description="매장명")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    road_addr: str = Field(..., description="도로명 주소")
    review_avg_score: float = Field(..., description="리뷰 평균 평점")
    review_cnt: int = Field(..., description="리뷰 총 수")
    distance_km: float = Field(..., description="거리 (km)")
    thumbnail_url: Optional[str] = Field(..., description="대표 썸네일")
    categories: List[str] = Field(..., description="카테고리 해시태그 목록")

class NearbyScrollResponse(BaseModel):
    items: list[NearbyStudioItem] = Field(..., description="가까운 거리 목록")
    total: int = Field(..., description="항목 총 개수")
    offset: int = Field(..., description="스크롤 시작 위치")
    limit: int = Field(..., description="한 스크롤 당 기본 3개씩 표현")
    has_more: bool = Field(..., description="마지막 스크롤인지 판단하는 변수")


class RankedStudio(BaseModel):
    ps_id: int = Field(..., description="매장 ID")
    name: str = Field(..., description="매장 이름")
    avg_rating: float = Field(..., description="평균 리뷰 평점")
    review_cnt: int = Field(..., description="리뷰 개수")
    weighted_rating: float = Field(..., description="가중평균 점수")
    thumbnail_url: Optional[str] = Field(..., description="매장 대표 썸네일")
    rank: int = Field(..., description="매장 랭킹")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")

    class Config:
        orm_mode = True

class PhotoStudioDetail(BaseModel):
    ps_id: int = Field(..., description="매장 ID")
    name: str = Field(..., description="매장 이름")
    avg_rating: float = Field(..., description="평균 리뷰 평점")
    review_count: int = Field(..., description="리뷰 개수")
    categories: List[str] = Field(..., description="카테고리 해시태그 목록")

    class Config:
        from_attributes = True

class PhotoStudioReviewImageResponse(BaseModel):
    review_id: int = Field(..., description="매장 이미지 ID")
    review_image: Optional[str] = Field(..., description="매장 이미지")

class PhotoStudioGalleryPage(BaseModel):
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="한 번 호출 시 불러올 최대 개수")
    has_more: bool = Field(..., description="마지막 페이지 확인 변수")
    images: List[PhotoStudioReviewImageResponse]