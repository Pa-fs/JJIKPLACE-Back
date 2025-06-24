from fastapi import Depends, APIRouter, UploadFile, File, Security
from sqlalchemy.orm import Session

from app.auth.jwt import get_current_user, bearer_scheme
from app.database import get_db
from app.services import profile_service

router = APIRouter()

@router.get("/profile/me",
            summary="프로필 정보 반환",
            description="이메일, 닉네임, 프로필 이미지 반환",
            dependencies=[Security(bearer_scheme)])
def my_profile(user= Depends(get_current_user)):
    return {"message": "인증 성공", "user": {
        "email": user["email"],
        "nickname": user["nick_name"],
        "profile_image": user.get("profile_image")
    }}

@router.patch("/profile/image",
              summary="프로필이미지 수정",
              description="이미지파일 포함해서 수정 요청 시 이미지링크 반환",
              dependencies=[Security(bearer_scheme)])
def update_profile_image(
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return profile_service.update_profile_image(db, user, image_file)
