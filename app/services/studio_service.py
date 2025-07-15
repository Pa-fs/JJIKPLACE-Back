from datetime import timedelta
from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import func, literal
from sqlalchemy.orm import Session

from app.dto.response.StudioResponseSchemas import RankedStudio, PhotoStudioDetail, PhotoStudioReviewImageResponse
from app.models import kst_now, Review, PhotoStudio, PhotoStudioImage, User, PhotoStudioCategory
from app.util.azure_upload import validate_image_upload, upload_file_to_azure, get_full_azure_url

def is_admin(db, user_info):
    user = db.query(User).filter(User.email == user_info["email"]).first()

    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.")

def get_studio_ranking(db, days, m, limit):

    POPULAR_CATEGORY_ID = 6

    """
    WR = (v / (v + m)) * R + (m / (v + m)) * C
        R : 스튜디오 평균 평점
        v : 스튜디오 리뷰 수
        m : 기준 리뷰 수
        C : 전체 평균 평점
    """

    since = kst_now() - timedelta(days=days)

    C = (
        db.query(func.avg(Review.rating))
        .filter(Review.created_at >= since)
        .scalar()
    ) or 0

    subq = (
        db.query(
            Review.ps_id.label("ps_id"),
            func.count(Review.review_id).label("v"),
            func.avg(Review.rating).label("R"),
        )
        .filter(Review.created_at >= since)
        .group_by(Review.ps_id)
        .subquery()
    )

    # WR 계산
    wr_expr = (
        (subq.c.v / (subq.c.v + literal(m))) * subq.c.R +
         (literal(m) / (subq.c.v + literal(m))) * C
    ).label("wr")

    studios = (
        db.query(
            PhotoStudio.ps_id,
            PhotoStudio.ps_name,
            PhotoStudio.thumbnail_url,
            subq.c.R,
            subq.c.v,
            wr_expr,
            PhotoStudio.lat,
            PhotoStudio.lng,
        )
        .join(subq, PhotoStudio.ps_id == subq.c.ps_id)
        .filter(subq.c.v >= m) # 최소 리뷰 수 m개 이상
        .order_by(wr_expr.desc(), subq.c.v.desc())
        .limit(limit)
        .all()
    )

    # 기존 인기태그 삭제 및 재등록
    db.query(PhotoStudioCategory) \
    .filter(PhotoStudioCategory.category_id == POPULAR_CATEGORY_ID) \
    .delete(synchronize_session=False)

    for s in studios:
        db.add(
            PhotoStudioCategory(
                ps_id=s.ps_id,
                category_id=POPULAR_CATEGORY_ID
            )
        )
    db.commit()


    result: list[RankedStudio] = []
    for idx, s in enumerate(studios, start= 1):
        result.append(
            RankedStudio(
            rank= idx,
            ps_id= s.ps_id,
            name= s.ps_name,
            avg_rating= round(s.R, 2),
            review_cnt= int(s.v),
            weighted_rating= round(s.wr, 3),
            thumbnail_url= get_full_azure_url(s.thumbnail_url) if s.thumbnail_url else None,
            lat= s.lat,
            lng= s.lng,
        )
    )

    return result


def verify_studio(db, ps_id):
    studio = db.query(PhotoStudio).filter(PhotoStudio.ps_id == ps_id).first()
    if not studio:
        raise HTTPException(404, "해당 사진관을 찾을 수 없습니다.")

    return studio


def add_studio_images(db: Session, ps_id: int, files: List[UploadFile], user_info):
    is_admin(db, user_info)

    studio = verify_studio(db, ps_id)

    uploaded_urls: list[str] = []

    for file in files:
        validate_image_upload(file)

        filename = upload_file_to_azure(file)
        full_url = get_full_azure_url(filename)
        uploaded_urls.append(full_url)

        img = PhotoStudioImage(
            ps_id=ps_id,
            ps_image=filename,
            description=None
        )
        db.add(img)
    db.commit()
    return uploaded_urls


def add_studio_thumbnail(db: Session, ps_id: int, file: UploadFile, user_info):
    is_admin(db, user_info)

    studio = verify_studio(db, ps_id)

    validate_image_upload(file)

    filename = upload_file_to_azure(file)
    full_url = get_full_azure_url(filename)

    studio.thumbnail_url = filename
    db.commit()

    return {
        "message": "썸네일이 업데이트 되었습니다.",
        "thumbnail_url": full_url
    }


def get_studio_detail(db, ps_id):
    studio = verify_studio(db, ps_id)

    avg_rating = db.query(func.avg(Review.rating)).filter(Review.ps_id == ps_id).scalar() or 0.0
    review_count = db.query(func.count(Review.review_id)).filter(Review.ps_id == ps_id).scalar()

    tags = [f"#{pc.category.name}" for pc in studio.categories]

    return PhotoStudioDetail(
        ps_id=studio.ps_id,
        name=studio.ps_name,
        avg_rating=round(avg_rating, 1),
        review_count=review_count,
        categories=tags
    )


def get_studio_gallery_page(db, ps_id, page, size):
    verify_studio(db, ps_id)

    # total = db.query(func.count(PhotoStudioImage.psi_id)) \
    #             .filter(PhotoStudioImage.ps_id == ps_id) \
    #             .scalar() or 0

    total = (
        db.query(func.count(Review.review_id))
        .filter(Review.ps_id == ps_id)
        .filter(Review.image_url != None)
        .scalar()
    ) or 0

    offset = (page - 1) * size

    # images = (
    #     db.query(PhotoStudioImage)
    #     .filter(PhotoStudioImage.ps_id == ps_id)
    #     .order_by(PhotoStudioImage.psi_id)
    #     .offset(offset)
    #     .limit(size)
    #     .all()
    # )

    reviews = (
        db.query(Review.review_id, Review.image_url)
        .filter(Review.ps_id == ps_id)
        .filter(Review.image_url != None)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    # dto_list = [
    #     PhotoStudioImageResponse(
    #         psi_id = img.psi_id,
    #         studio_image = get_full_azure_url(img.ps_image) if img.ps_image else None,
    #         description = img.description
    #     )
    #     for img in images
    # ]

    dto_list = []
    for review_id, filename in reviews:
        dto_list.append(
            PhotoStudioReviewImageResponse(
                review_id=review_id,
                review_image=get_full_azure_url(filename),
            )
        )

    has_more = (offset + len(dto_list)) < total

    return dto_list, has_more