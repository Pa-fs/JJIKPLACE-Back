from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config(".env")

oauth = OAuth(config)

kakao = oauth.register(
    name= "kakao",
    client_id= config("KAKAO_CLIENT_ID"),
    client_secret= config("KAKAO_CLIENT_SECRET"),
    authorize_url='https://kauth.kakao.com/oauth/authorize',
    access_token_url='https://kauth.kakao.com/oauth/token',
    api_base_url='https://kapi.kakao.com',
    client_kwargs={'scope': 'profile_nickname account_email'},
    token_endpoint_auth_method="client_secret_post",
)

# naver = oauth.register(
#     name="naver",
#     client_id=config("NAVER_CLIENT_ID"),
#     client_secret=config("NAVER_CLIENT_SECRET"),
#     authorize_url="https://nid.naver.com/oauth2.0/authorize",
#     access_token_url="https://nid.naver.com/oauth2.0/token",
#     api_base_url="https://openapi.naver.com",
#     client_kwargs={"scope": "name email"}
# )

google = oauth.register(
    name="google",
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    api_base_url="https://openidconnect.googleapis.com/v1/",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "consent",  # 안 넣으면 refresh 토큰 안 줌
        "access_type": "offline",
    },
    token_endpoint_auth_method="client_secret_post",
)

KAKAO_REDIRECT_URI = config("KAKAO_REDIRECT_URI")
# NAVER_REDIRECT_URI = config("NAVER_REDIRECT_URI")
GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI")