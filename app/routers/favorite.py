from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user
from app.database import get_db
from app.services import favorite_service

router = APIRouter()

@router.post("/favorite/{ps_id}",
             summary="찜 추가")
def add_favorite(
    ps_id: int,
    db: Session = Depends(get_db),
    user_info= Depends(get_current_user)
):
    return favorite_service.add_favorite(ps_id, db, user_info)

@router.delete("/favorite/{ps_id}",
            summary="찜 삭제")
def remove_favorite(
    ps_id: int,
    db: Session = Depends(get_db),
    user_info=Depends(get_current_user)
):
    return favorite_service.remove_favorite(ps_id, db, user_info)