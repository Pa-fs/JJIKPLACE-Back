from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_200_OK

from app.auth.jwt import get_current_user

router = APIRouter()

@router.get("/profile/me")
def my_profile(user= Depends(get_current_user)):
    return {"message": "인증 성공", "user": user}

def response_jwt_in_cookie(redirect_url: str, jwt_token: str):
    # response = RedirectResponse(redirect_url) # CORS 문제 야기함

    response_body = {
        "status": "success",
        "code": HTTP_200_OK,
        "message": "로그인 성공"
    }

    response = JSONResponse(
        content=response_body,
        status_code=HTTP_200_OK
    )

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=False, # HTTPS 인 경우 True
        samesite="Lax" # CSRF 방지용
    )
    return response