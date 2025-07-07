from pydantic import BaseModel, Field
from typing import List, Optional


class ClusterItem(BaseModel):
    name: str = Field(..., description="클러스터 이름 (예: 서울 강남구)")
    count: int = Field(..., description="해당 구역의 사진관 수")
    lat: float = Field(..., description="클러스터 중심 평균 위도")
    lng: float = Field(..., description="클러스터 중심 평균 경도")

class ClusterResponse(BaseModel):
    level: str = Field(..., description="클러스터링 단위 (예: sido, gungu, dongmyeon")
    clusters: List[ClusterItem]


class MarkerItem(BaseModel):
    id: int = Field(..., description="매장 ID")
    name: str = Field(..., description="매장 이름")
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    road_addr: str = Field(..., description="도로명 주소")
    review_avg_score: float = Field(..., description="리뷰 평점")
    review_cnt: int = Field(..., description="리뷰 개수")
    thumbnail_url: Optional[str] = Field(..., description="대표 썸네일")
    categories: List[str] = Field(..., description="카테고리 해시태그 목록")
    is_favorite: bool = Field(..., description="내 찜 여부")

class MarkerResponse(BaseModel):
    level: str = Field(default="marker", description="클러스터링 레벨")
    markers: List[MarkerItem]