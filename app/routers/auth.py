from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/profile/me")
def my_profile(user= Depends(get_current_user)):
    return {"message": "인증 성공", "user": user}