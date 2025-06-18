from fastapi import FastAPI
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.database import engine
from app import models
from app.routers import cluster, sns_auth, form_auth, review, studios

config = Config(".env")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key= config("JWT_SECRET_KEY"))

app.include_router(cluster.router, prefix="/cluster", tags=["지도 클러스터링 API"])
app.include_router(studios.router, tags=["지도 클러스터링 API"])
app.include_router(sns_auth.router, tags=["로그인 API"])
app.include_router(form_auth.router, tags=["로그인 API"])
app.include_router(review.router, tags=["리뷰 API"])

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # 쿠키 및 tls 에 필요
    allow_methods=["*"],
    allow_headers=["*"],
)