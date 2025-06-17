from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_serializer


class ReviewItem(BaseModel):
    review_id: int = Field(2124973472, description="리뷰 ID")
    rating: float = Field(..., description="리뷰 평점")
    content: Optional[str] = Field(..., description="리뷰 내용")
    created_at: datetime = Field(..., description="리뷰 생성일")
    user_nickname: str = Field(..., description="리뷰 작성자")

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return dt.strftime("%Y.%m.%d")

class ReviewScrollResponse(BaseModel):
    items: List[ReviewItem]
    total: int = Field(..., description="리뷰 총 개수")
    offset: int = Field(..., description="무한스크롤을 위한 오프셋 0, 4, 8 ...")
    limit: int = Field(..., description="한 페이지당 기본 4개씩 표현")
    has_more: bool = Field(..., description="마지막 스크롤인지 판단하는 변수")