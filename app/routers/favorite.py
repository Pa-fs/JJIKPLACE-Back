from typing import List

from fastapi import APIRouter, Depends
from fastapi.params import Security
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, bearer_scheme
from app.database import get_db
from app.dto.response.FavoriteResponseSchemas import FavoriteStudioResponse
from app.services import favorite_service

router = APIRouter()

@router.get("/favorite",
            summary="내가 찜한 매장 목록",
            response_model=List[FavoriteStudioResponse])
def list_favorites(
    db: Session = Depends(get_db),
    user_info=Depends(get_current_user)
):
    return favorite_service.list_favorites(db, user_info)

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