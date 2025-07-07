from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_serializer


class FavoriteStudioResponse(BaseModel):
    ps_id: int = Field(..., description="매장 식별 ID")
    name: str = Field(..., description="매장명")
    thumbnail_url: Optional[str] = Field(..., description="대표 썸네일")
    road_addr: str = Field(..., description="도로명 주소")
    created_at: datetime = Field(..., description="찜한 날짜")

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return dt.strftime("%Y.%m.%d")

class FavoritePage(BaseModel):
    items: List[FavoriteStudioResponse] = Field(..., description="찜한 매장 리스트")
    total: int = Field(..., description="전체 찜 갯수")
    offset: int = Field(..., description="시작 위치")
    size: int = Field(..., description="한 번에 불러올 개수")
    has_more: bool = Field(..., description="추가 데이터 존재 여부")