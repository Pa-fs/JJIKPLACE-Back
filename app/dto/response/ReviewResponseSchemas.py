from fastapi import Form
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_serializer


class ReviewItem(BaseModel):
    review_id: int = Field(2124973472, description="리뷰 ID")
    rating: float = Field(..., description="리뷰 평점")
    content: Optional[str] = Field(..., description="리뷰 내용")
    image_url: Optional[str] = Field(..., description="리뷰 이미지")
    created_at: datetime = Field(..., description="리뷰 생성일")
    user_nickname: str = Field(..., description="리뷰 작성자")

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return dt.strftime("%Y.%m.%d")

class ReviewScrollResponse(BaseModel):
    items: List[ReviewItem]
    total: int = Field(..., description="리뷰 총 개수")
    offset: int = Field(..., description="스크롤 시작 위치")
    limit: int = Field(..., description="한 스크롤 당 기본 4개씩 표현")
    has_more: bool = Field(..., description="마지막 스크롤인지 판단하는 변수")


# 리뷰 등록
class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=0, le=5, description="리뷰 평점")
    content: Optional[str] = Field(default=None, description="리뷰 내용")
    ps_id: int = Field(..., description="매장 ID")

    @classmethod
    def as_form(cls,
                rating: float = Form(description="리뷰 평점", ge=0, le=5),
                content: Optional[str] = Form(None, description="리뷰 내용", example=None), # 선택 입력
                ps_id: int = Form(description="매장 ID")):
        return cls(rating=rating, content=content, ps_id=ps_id)


class ReviewResponse(BaseModel):
    review_id: int = Field(2124973472, description="리뷰 ID")
    rating: float = Field(..., description="리뷰 평점")
    content: Optional[str] = Field(..., description="리뷰 내용")
    image_url: Optional[str] = Field(..., description="리뷰 이미지")
    created_at: datetime = Field(..., description="리뷰 생성일")
    updated_at: datetime
    user_id: int
    ps_id: int

class MyReviewResponse(BaseModel):
    review_id: int = Field(2124973472, description="리뷰 ID")
    rating: float = Field(..., description="리뷰 평점")
    content: Optional[str] = Field(..., description="리뷰 내용")
    image_url: Optional[str] = Field(..., description="리뷰 이미지")
    created_at: datetime = Field(..., description="리뷰 생성일")
    updated_at: datetime = Field(..., description="리뷰 수정일")
    ps_id : int = Field(..., description="매장 ID")
    name: str = Field(..., description="매장 이름")

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info) -> str:
        return dt.strftime("%Y.%m.%d")

class ReviewPage(BaseModel):
    total: int = Field(..., description="리뷰 총 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 당 개수")
    has_more: bool = Field(..., description="마지막 페이지 확인 변수")
    items: List[MyReviewResponse] = Field(..., description="리뷰 목록")