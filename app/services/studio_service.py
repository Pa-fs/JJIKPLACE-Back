from datetime import timedelta
from typing import List

from fastapi import UploadFile, HTTPException
from sqlalchemy import func, literal
from sqlalchemy.orm import Session

from app.dto.response.StudioResponseSchemas import RankedStudio
from app.models import kst_now, Review, PhotoStudio, PhotoStudioImage, User
from app.util.azure_upload import validate_image_upload, upload_file_to_azure, get_full_azure_url

def is_admin(db, user_info):
    admin_user = "test96@naver.com" == user_info["email"]
    verified = db.query(User).filter(User.email == "test96@naver.com")
    if not admin_user or not verified:
        raise HTTPException(400, "해당 권한이 없습니다.")

def get_studio_ranking(db, days, m, limit):
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
            subq.c.R,
            subq.c.v,
            wr_expr
        )
        .join(subq, PhotoStudio.ps_id == subq.c.ps_id)
        .filter(subq.c.v >= m) # 최소 리뷰 수 m개 이상
        .order_by(wr_expr.desc(), subq.c.v.desc())
        .limit(limit)
        .all()
    )

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
            image_url= None
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