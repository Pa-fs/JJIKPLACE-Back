import os
from fastapi import Request, HTTPException, status
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
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다. 다시 로그인 해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_jwt_token(token)