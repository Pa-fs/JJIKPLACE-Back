from fastapi import Depends, HTTPException, APIRouter
from fastapi.params import Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.auth.hash import hash_password
from app.database import get_db
from app.models import User

router = APIRouter()

class FormSignUp(BaseModel):
    email: EmailStr
    password: str
    nick_name: str

@router.post("/auth/signup",
             summary="폼 회원가입")
def form_signup(form: FormSignUp, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == form.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    user = User(
        email= form.email,
        password= hash_password(form.password),
        nick_name= form.nick_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "회원가입 완료"}


@router.post("/auth/signup/check-email",
             summary="이메일중복 확인")
def check_email_availability(db: Session = Depends(get_db),
                             email: EmailStr = Query(...)):
    existing_user = db.query(User).filter(User.email == email).first()

    return {
        "available": existing_user is None,
        "message": "사용 가능한 이메일입니다." if existing_user is None else "이미 사용 중인 이메일입니다."
    }