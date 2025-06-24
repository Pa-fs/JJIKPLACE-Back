from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_jwt_token
from app.database import get_db
from app.models import User
from app.routers.auth import response_jwt_in_cookie
from app.util.allowed_front_urls import get_safe_redirect_url

router = APIRouter()

class FormLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth/login",
             summary="폼 로그인")
def form_login(request: Request, form: FormLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    access_token = create_jwt_token(user.email, user.nick_name, user.profile_image)
    # redirect_url = get_safe_redirect_url(request)
    return {"access_token": access_token, "token_type": "Bearer"}