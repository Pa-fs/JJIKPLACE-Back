from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import User
from app.util.azure_upload import get_full_azure_url


def get_filtered_markers(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float, user_info, category=None):
    user_id = None
    if user_info:
        u = db.query(User).filter(User.email == user_info["email"]).first()
        user_id = u.user_id if u else None

    base_sql = """
        SELECT
          ps.ps_id   AS id,
          ps.ps_name AS name,
          ps.lat,
          ps.lng,
          ps.road_addr,
          COALESCE(ROUND(AVG(r.rating), 1), 0) AS review_avg_score,
          COUNT(r.review_id)      AS review_cnt,
          ps.thumbnail_url,
          GROUP_CONCAT(DISTINCT c.name) AS category_list,
          CASE WHEN fs.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_favorite
        FROM photo_studios ps
        LEFT JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
        LEFT JOIN category c                ON psc.category_id = c.category_id
        LEFT JOIN review r                  ON r.ps_id = ps.ps_id
        LEFT JOIN favorite_studio fs        ON fs.ps_id = ps.ps_id AND fs.user_id = :user_id
    """

    where_sql = """
        WHERE CAST(ps.lat AS FLOAT) BETWEEN :sw_lat AND :ne_lat
          AND CAST(ps.lng AS FLOAT) BETWEEN :sw_lng AND :ne_lng
    """

    if category:
        where_sql += " AND c.name = :category"

    group_sql = " GROUP BY ps.ps_id ORDER BY name"

    full_sql = text(base_sql + where_sql + group_sql)

    params = {
        "sw_lat": sw_lat,
        "ne_lat": ne_lat,
        "sw_lng": sw_lng,
        "ne_lng": ne_lng,
        "user_id": user_id,
    }
    if category:
        params["category"] = category

    rows = db.execute(full_sql, params).mappings().all()

    markers = []
    for row in rows:
        d = dict(row)

        # 썸네일 full URL
        thumb = d.get("thumbnail_url")
        d["thumbnail_url"] = get_full_azure_url(thumb) if thumb else None

        # 해시태그 변환
        raw = d.pop("category_list", "") or ""
        d["categories"] = [f"#{n.strip()}" for n in raw.split(",") if n.strip()]

        # is_favorite 이미 bool
        markers.append(d)

    return {
        "level": "marker",
        "markers": markers
    }