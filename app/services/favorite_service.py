from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dto.response.FavoriteResponseSchemas import FavoriteStudioResponse
from app.models import PhotoStudio, FavoriteStudio
from app.services.profile_service import verify_user
from app.util.azure_upload import get_full_azure_url



def list_favorites_paginated(db: Session, user_info: dict, offset: int, size: int):
    user = verify_user(db, user_info)

    total = (
        db.query(func.count(FavoriteStudio.fs_id))
          .filter(FavoriteStudio.user_id == user.user_id)
          .scalar()
    ) or 0

    rows = (
        db.query(
            PhotoStudio.ps_id,
            PhotoStudio.ps_name,
            PhotoStudio.thumbnail_url,
            PhotoStudio.road_addr,
            FavoriteStudio.created_at.label("created_at"),
        )
        .join(FavoriteStudio, FavoriteStudio.ps_id == PhotoStudio.ps_id)
        .filter(FavoriteStudio.user_id == user.user_id)
        .order_by(FavoriteStudio.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    items = []
    for ps_id, name, thumb, road_addr, created_at in rows:
        items.append(
            FavoriteStudioResponse(
                ps_id=ps_id,
                name=name,
                thumbnail_url=get_full_azure_url(thumb) if thumb else None,
                road_addr=road_addr,
                created_at=created_at,
            )
        )

    has_more = (offset + len(items)) < total

    return items, total, has_more


def add_favorite(ps_id, db, user_info):
    user = verify_user(db, user_info)
    exists = db.query(FavoriteStudio) \
            .filter_by(user_id=user.user_id, ps_id=ps_id) \
            .first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 찜한 매장입니다."
        )

    fav = FavoriteStudio(user_id=user.user_id, ps_id=ps_id)
    db.add(fav)
    db.commit()
    return {"message": "찜에 추가되었습니다."}


def remove_favorite(ps_id, db, user_info):
    user = verify_user(db, user_info)
    deleted = db.query(FavoriteStudio) \
               .filter_by(user_id=user.user_id, ps_id=ps_id) \
               .delete()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="찜한 매장이 아닙니다."
        )

    db.commit()
    return {"message": "찜에서 삭제되었습니다."}