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

class FormSignUp(BaseModel):
    email: EmailStr
    password: str
    nick_name: str

@router.post("/auth/signup")
def form_signup(form: FormSignUp, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == form.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    user = User(
        email= form.email,
        password= hash_password(form.password),
        nick_name= form.nick_name,
        created_at= datetime.utcnow(),
        updated_at= datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "회원가입 완료"}

class FormLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth/login")
def form_login(request: Request, form: FormLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    jwt_token = create_jwt_token(user.user_id, user.email)
    redirect_url = get_safe_redirect_url(request)
    return response_jwt_in_cookie(redirect_url, jwt_token)