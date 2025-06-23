from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

def response_jwt_in_cookie(redirect_url, jwt_token: str):
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