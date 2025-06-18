from sqlalchemy.orm import Session
from app.models import PhotoStudio, Category, PhotoStudioCategory
from sqlalchemy import func, Float


def cluster(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float, category: str = None):
    query = db.query(
        PhotoStudio.sido,
        func.count().label("count"),
        func.avg(PhotoStudio.lat.cast(Float)).label("center_lat"),
        func.avg(PhotoStudio.lng.cast(Float)).label("center_lng")
    )

    if category:
        query = query.join(PhotoStudioCategory, PhotoStudio.ps_id == PhotoStudioCategory.ps_id) \
        .join(Category, Category.category_id == PhotoStudioCategory.category_id) \
        .filter(Category.name == category)

    query = query.filter(
        PhotoStudio.lat.cast(Float).between(sw_lat, ne_lat),
        PhotoStudio.lng.cast(Float).between(sw_lng, ne_lng)
    ).group_by(PhotoStudio.sido)

    clusters = [
        {
            "name": row.sido,
            "count": row.count,
            "lat": row.center_lat,
            "lng": row.center_lng
        }
        for row in query.all()
    ]
    return {"level": "sido", "clusters": clusters}