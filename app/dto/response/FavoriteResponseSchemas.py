from datetime import datetime
from typing import Optional

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