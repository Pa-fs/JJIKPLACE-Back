import datetime
import os
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import timedelta
from dotenv import load_dotenv

from app.util.azure_upload import get_full_azure_url

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=True)

def create_jwt_token(email: str, nickname: str, profile_image: str = None):
    payload = {
        # "sub": str(user_id),
        "email": email,
        "exp": datetime.datetime.utcnow() + timedelta(minutes=15),
        "nick_name": nickname
    }

    if profile_image:
        payload["profile_image"] = get_full_azure_url(profile_image)

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):

    # authorization = credentials.credentials
    # print(authorization)
    # if not authorization or not authorization.startswith("Bearer "):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="인증 정보가 없습니다.",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    token = credentials.credentials
    return decode_jwt_token(token)