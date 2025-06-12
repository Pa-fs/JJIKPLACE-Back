from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.hash import hash_password, verify_password
from app.auth.jwt import create_jwt_token
from app.database import get_db
from app.models import User

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
def form_login(form: FormLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.email).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    token = create_jwt_token(user.user_id, user.email)
    return {"access_token": token, "token_type": "bearer"}