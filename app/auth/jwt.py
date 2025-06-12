import os
from urllib.request import Request

from fastapi import HTTPException, status
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def create_jwt_token(user_id: int, email: str):
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes= 15)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm= ALGORITHM)

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "토큰이 만료되었습니다. 다시 로그인 해주세요.",
            headers= {"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers= {"WWW-Authenticate": "Bearer"},
        )

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "인증 정보가 없습니다.",
            headers= {"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]
    return decode_jwt_token(token)