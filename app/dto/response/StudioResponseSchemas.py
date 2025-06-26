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
    image_url: Optional[str] = Field(..., description="매장 대표 이미지")
    rank: int = Field(..., description="매장 랭킹")

    class Config:
        orm_mode = True