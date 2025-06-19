import datetime

from fastapi import UploadFile, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dto.response.ReviewResponseSchemas import ReviewCreate
from app.models import Review
from app.util.azure_upload import upload_file_to_azure, get_full_azure_url


def get_review_details_in_photo_studio(db: Session, ps_id: int, offset: int, limit: int):
    try:
        sql = text("""
        SELECT
            r.review_id,
            r.rating,
            r.content,
            r.created_at,
            u.nick_name AS user_nickname
        FROM review r
        INNER JOIN user u ON r.user_id = u.user_id
        WHERE r.ps_id = :ps_id
        ORDER BY r.created_at DESC
        LIMIT :limit OFFSET :offset
        """)

        result = db.execute(sql, {
            "ps_id": ps_id,
            "limit": limit,
            "offset": offset
        }).mappings().all()

        count_sql = text("SELECT COUNT(*) FROM review WHERE ps_id = :ps_id")
        total = db.execute(count_sql, {"ps_id": ps_id}).scalar()

        return {
            "items": result,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(result) < total
        }
    except Exception as e:
        print(f"리뷰 목록 조회 시 에러 발생: {e}")
        return []

# 리뷰 등록
def create_review(db: Session, data: ReviewCreate, user_id: int, image_file: UploadFile):
    image_url = None

    if image_file and image_file != "":
        try:
            image_filename = upload_file_to_azure(image_file)
            image_url = image_filename # DB에 저장
        except Exception as e:
            raise HTTPException(status_code=500, detail="이미지 업로드 실패: " + str(e))

    review = Review(
        rating=data.rating,
        content=data.content,
        image_url=image_url,
        user_id=user_id,
        ps_id=data.ps_id
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    full_image_url = get_full_azure_url(image_url) if image_url else None

    return {
        "review_id": review.review_id,
        "rating": review.rating,
        "content": review.content,
        "image_url": full_image_url,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
        "user_id": review.user_id,
        "ps_id": review.ps_id,
    }