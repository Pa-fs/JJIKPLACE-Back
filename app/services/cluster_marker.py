from sqlalchemy import func, Float, cast, text
from sqlalchemy.orm import Session
from app.models import PhotoStudio, Review

def get_markers(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float):
    # subq = (
    #     db.query(
    #         Review.ps_id.label("ps_id"),
    #         func.avg(Review.rating).label("review_avg_score"),
    #         func.count(Review.review_id).label("review_cnt")
    #     )
    #     .group_by(Review.ps_id)
    #     .subquery()
    # )
    #
    # result = (
    #     db.query(
    #         PhotoStudio.ps_id.label("id"),
    #         PhotoStudio.ps_name.label("name"),
    #         PhotoStudio.lat,
    #         PhotoStudio.lng,
    #         PhotoStudio.road_addr,
    #         func.coalesce(subq.c.review_avg_score, 0).label("review_avg_score"),
    #         func.coalesce(subq.c.review_cnt, 0).label("review_cnt")
    #     )
    #     .outerjoin(subq, PhotoStudio.ps_id == subq.c.ps_id)
    #     .filter(cast(PhotoStudio.lat, Float).between(sw_lat, ne_lat))
    #     .filter(cast(PhotoStudio.lng, Float).between(sw_lng, ne_lng))
    #     .all()
    # )

    # return {
    #     "level": "marker",
    #     "markers": [dict(row._mapping) for row in result]
    # }

    sql = text("""
    SELECT
        ps.ps_id AS id,
        ps.ps_name AS name,
        ps.lat,
        ps.lng,
        ps.road_addr,
        COALESCE(AVG(r.rating), 0) AS review_avg_score,
        COUNT(r.review_id) AS review_cnt
    FROM photo_studios ps
    LEFT JOIN review r ON r.ps_id = ps.ps_id
    WHERE CAST(ps.lat AS FLOAT) BETWEEN :sw_lat AND :ne_lat
      AND CAST(ps.lng AS FLOAT) BETWEEN :sw_lng AND :ne_lng
    GROUP BY ps.ps_id
    """)

    result = db.execute(sql, {
        "sw_lat": sw_lat,
        "ne_lat": ne_lat,
        "sw_lng": sw_lng,
        "ne_lng": ne_lng,
    }).mappings().all()

    return {
        "level": "marker",
        "markers": result  # FastAPI에서 DTO로 자동 변환
    }