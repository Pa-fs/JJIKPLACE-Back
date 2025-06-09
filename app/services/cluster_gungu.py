from sqlalchemy.orm import Session
from app.models import PhotoStudio
from sqlalchemy import func

def cluster(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float):
    query = db.query(
        PhotoStudio.sido,
        PhotoStudio.gungu,
        func.count().label("count"),
        func.avg(PhotoStudio.lat).label("center_lat"),
        func.avg(PhotoStudio.lng).label("center_lng")
    ).filter(
        PhotoStudio.lat.between(sw_lat, ne_lat),
        PhotoStudio.lng.between(sw_lng, ne_lng)
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