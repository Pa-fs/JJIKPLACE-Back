from fastapi import HTTPException, status

from app.dto.response.FavoriteResponseSchemas import FavoriteStudioResponse
from app.models import PhotoStudio, FavoriteStudio
from app.services.profile_service import verify_user
from app.util.azure_upload import get_full_azure_url


def list_favorites(db, user_info):
    user = verify_user(db, user_info)

    rows = db.query(
        PhotoStudio.ps_id,
        PhotoStudio.ps_name,
        PhotoStudio.thumbnail_url,
        PhotoStudio.road_addr,
        FavoriteStudio.created_at.label("created_at"),
    ).join(FavoriteStudio, FavoriteStudio.ps_id == PhotoStudio.ps_id
    ).filter(FavoriteStudio.user_id == user.user_id
    ).order_by(FavoriteStudio.created_at.desc()
    ).all()

    return [
        FavoriteStudioResponse(
            ps_id=r.ps_id,
            name=r.ps_name,
            thumbnail_url=get_full_azure_url(r.thumbnail_url) if r.thumbnail_url else None,
            road_addr=r.road_addr,
            created_at=r.created_at
        ) for r in rows
    ]


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