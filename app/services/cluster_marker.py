from sqlalchemy.orm import Session
from app.models import PhotoStudio

def get_markers(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float):
    studios = db.query(PhotoStudio).filter(
        PhotoStudio.lat.between(sw_lat, ne_lat),
        PhotoStudio.lng.between(sw_lng, ne_lng)
    ).all()

    return {
        "level": "marker",
        "markers": [
            {
                "id": s.ps_id,
                "name": s.ps_name,
                "lat": s.lat,
                "lng": s.lng
            } for s in studios
        ]
    }