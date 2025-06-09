from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.crawling_savedb import save_studio_and_reviews
from app.database import SessionLocal, engine
from app import models, kakao
from app.models import PhotoStudio
from app.routers import cluster

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(cluster.router, prefix="/cluster", tags=["지도 클러스터링 API"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 무료플랜: 카카오 키워드검색 API 한 번 요청 시 45개로 제한 (3 페이지)
# @app.post("/crawl")
# def crawl_and_store(keyword: str = "셀프사진관", db: Session = Depends(get_db)):
def crawl_and_store():
    sido_gungu = [
        ("광주광역시", "광산구"), ("광주광역시", "북구"), ("광주광역시", "동구"),
        ("전라북도", "전주시"), ("전라북도", "군산시"), ("전라북도", "익산시"),
        ("전라남도", "여수시"), ("전라남도", "순천시"), ("전라남도", "목포시"),
        ("부산광역시", "남구"), ("부산광역시", "동래구"),
        ("대구광역시", "중구"), ("대구광역시", "수성구"), ("대구광역시", "달서구"), ("대구광역시", "북구"),
        ("인천광역시", "연수구"), ("인천광역시", "남동구"), ("인천광역시", "부평구"), ("인천광역시", "서구"),
        ("광주광역시", "동구"), ("광주광역시", "서구"), ("광주광역시", "남구"), ("광주광역시", "북구"),
        ("대전광역시", "서구"), ("대전광역시", "유성구"), ("대전광역시", "중구"), ("대전광역시", "동구"),
        ("울산광역시", "남구"), ("울산광역시", "중구"), ("울산광역시", "북구"), ("울산광역시", "동구"),
        ("경기도", "수원시"), ("경기도", "성남시"), ("경기도", "고양시"), ("경기도", "용인시"),
        ("강원도", "춘천시"), ("강원도", "원주시"), ("강원도", "강릉시"),
        ("충청북도", "청주시"), ("충청북도", "충주시"), ("충청북도", "제천시"),
        ("충청남도", "천안시"), ("충청남도", "아산시"), ("충청남도", "서산시"),
        ("경상북도", "포항시"), ("경상북도", "경주시"), ("경상북도", "구미시"),
        ("경상남도", "창원시"), ("경상남도", "김해시"), ("경상남도", "진주시"),
        ("제주특별자치도", "제주시"), ("제주특별자치도", "서귀포시")
    ]

    db = SessionLocal()
    stored_count = 0
    page = 1
    size = 15
    is_end = False

    for sido, gungu in sido_gungu:
        keyword = f"{gungu} 셀프사진관"
        page = 1
        size = 15
        is_end = False
        print(f"✅ [{sido} {gungu}] 지역 크롤링 시작")

        while not is_end:
            # 검색 결과
            response = kakao.search_photo_studios(keyword, page=page, size=size)
            results = response.get("documents", [])
            meta = response.get("meta", {})
            # 반복 종료 조건
            is_end = meta.get("is_end", True)

            print("page:", page)
            print("is_end:", meta.get("is_end"))
            print("total_count:", meta.get("total_count"))
            print("pageable_count:", meta.get("pageable_count"))

            if not results:
                break

            for item in results:
                place_id = item["id"]

                exists = db.query(PhotoStudio).filter_by(kakao_id=place_id).first()
                if exists:
                    print(f"이미 존재하는 place_id {place_id} 건너뛰기")
                    continue

                studio_data = {
                    "ps_id": int(place_id),
                    "ps_name": item["place_name"],
                    "road_addr": item.get("road_address_name"),
                    "addr": item.get("address_name"),
                    "phone": item.get("phone"),
                    "lat": item["y"],
                    "lng": item["x"],
                    "kakao_id": place_id,
                    "thumbnail_url": None,
                    "created_at": None,
                    "updated_at": None
                }

                save_studio_and_reviews(db, studio_data, place_id)

                stored_count += 1

            if is_end:
                break
            page += 1
        return {"stored": stored_count}

if __name__ == "__main__":
    crawl_and_store()