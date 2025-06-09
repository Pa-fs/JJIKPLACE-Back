from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.database import SessionLocal, engine
from app import models, kakao
from app.routers import cluster

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(cluster.router, prefix="/cluster", tags=["지도 클러스터링 API"])

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=True, 쿠키 및 tls 는 나중에 고려
    allow_methods=["*"],
    allow_headers=["*"],
)