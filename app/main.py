from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.crawling_savedb import save_studio_and_reviews
from app.database import SessionLocal, engine
from app import models, kakao

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/crawl")
def crawl_and_store(keyword: str = "셀프사진관", db: Session = Depends(get_db)):
    results = kakao.search_photo_studios(keyword)
    stored_count = 0

    for item in results:
        place_id = item["id"]

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
    return {"stored": stored_count}