from sqlalchemy.orm import Session
from app.models import PhotoStudio
from sqlalchemy import func

def cluster(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float):
    query = db.query(
        PhotoStudio.sido,
        func.count().label("count"),
        func.avg(PhotoStudio.lat).label("center_lat"),
        func.avg(PhotoStudio.lng).label("center_lng")
    ).filter(
        PhotoStudio.lat.between(sw_lat, ne_lat),
        PhotoStudio.lng.between(sw_lng, ne_lng)

    ).group_by(PhotoStudio.sido).all()

    clusters = [
        {
            "name": row.sido,
            "count": row.count,
            "lat": row.center_lat,
            "lng": row.center_lng
        }
        for row in query
    ]
    return {"level": "sido", "clusters": clusters}