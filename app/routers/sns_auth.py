from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette import status

from app.auth.jwt import create_jwt_token
from app.auth.oauth import KAKAO_REDIRECT_URI, kakao, google, GOOGLE_REDIRECT_URI
from app.database import get_db
from app.models import User, kst_now
from app.routers.auth import response_jwt_in_cookie
from app.util.allowed_front_urls import get_safe_redirect_url

router = APIRouter()

def get_or_create_user(db: Session, sns_type, sns_id, sns_email):
    user = (
        db.query(User)
        .filter((User.sns_id == sns_id) | (User.sns_email == sns_email))
        .first()
    )
    if not user:
        user = User(
            sns_type= sns_type,
            sns_id= sns_id,
            sns_email= sns_email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    if user and user.sns_id != sns_id:
        user.sns_id = sns_id
        user.sns_type = sns_type
        user.updated_at = kst_now()
        db.commit()
        db.refresh(user)
    return user

@router.get("/auth/kakao/login")
async def login_via_kakao(request: Request):
    return await kakao.authorize_redirect(request, KAKAO_REDIRECT_URI)

@router.get("/auth/kakao/callback")
async def callback_via_kakao(request: Request, db: Session = Depends(get_db)):
    print(f"KAKAO LOGIN SESSION VALUE: {request.session}")

    token = await kakao.authorize_access_token(request)
    user_info = await kakao.get("v2/user/me", token= token)
    kakao_user = user_info.json()

    try:
        kakao_id = str(kakao_user["id"])
        kakao_email = kakao_user["kakao_account"]["email"]
    except KeyError:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "카카오에서 이메일 정보를 가져올 수 없습니다. 필수 동의를 확인하세요"
        )

    user = get_or_create_user(db, sns_type= "kakao", sns_id= kakao_id, sns_email= kakao_email)

    jwt_token = create_jwt_token(user.user_id, user.email)

    redirect_url = get_safe_redirect_url(request)
    return response_jwt_in_cookie(redirect_url, jwt_token)

# @router.get("/auth/naver/login")
# async def login_via_naver(request: Request):
#     return await naver.authorize_redirect(request, NAVER_REDIRECT_URI)
#
# @router.get("/auth/naver/callback")
# async def callback_via_naver(request: Request, db: Session = Depends(get_db)):
#     print(f"NAVER LOGIN SESSION VALUE: {request.session}")
#     token = await naver.authorize_access_token(request)
#     user_info = await naver.get("/v1/nid/me", token=token)
#     profile = user_info.json()
#
#     try:
#         user_id = profile["response"]["id"]
#         email = profile["response"]["email"]
#         nickname = profile["response"].get("nickname")
#     except KeyError:
#         raise HTTPException(status_code=400, detail="네이버 응답 파싱 실패")
#
#     user = get_or_create_user(db, "naver", user_id, email)
#
#     jwt_token = create_jwt_token(user.user_id, user.sns_email)
#
#     return {"access_token": jwt_token, "token_type": "Bearer"}

@router.get("/auth/google/login")
async def login_via_google(request: Request):
    return await google.authorize_redirect(request, GOOGLE_REDIRECT_URI)

@router.get("/auth/google/callback")
async def callback_via_google(
    request: Request,
    db: Session = Depends(get_db),
):
    token = await google.authorize_access_token(request)
    user_info = await google.get("userinfo", token=token)  # 구글에서 기본 유저정보 endpoint
    google_user = user_info.json()

    try:
        google_id = google_user["sub"]
        google_email = google_user.get("email")
    except KeyError:
        raise HTTPException(status_code=400, detail="구글 사용자 정보 파싱 실패")

    user = get_or_create_user(db, "google", google_id, google_email)

    jwt_token = create_jwt_token(user.user_id, user.sns_email)
    redirect_url = get_safe_redirect_url(request)
    return response_jwt_in_cookie(redirect_url, jwt_token)