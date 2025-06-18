from sqlalchemy.orm import Session
from app.models import PhotoStudio, PhotoStudioCategory, Category
from sqlalchemy import func, Float


def cluster(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float, category: str = None):
    query = db.query(
        PhotoStudio.sido,
        PhotoStudio.gungu,
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
    ).group_by(PhotoStudio.sido, PhotoStudio.gungu)

    return {
        "level": "gungu",
        "clusters": [
            {
                "name": f"{r.sido} {r.gungu}",
                "count": r.count,
                "lat": r.center_lat,
                "lng": r.center_lng
            } for r in query.all()
        ]
    }