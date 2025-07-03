from sqlalchemy import text
from sqlalchemy.orm import Session

from app.util.azure_upload import get_full_azure_url


def get_filtered_markers(db: Session, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float, category=None):
    if category:
        sql = text("""
        SELECT
            ps.ps_id AS id,
            ps.ps_name AS name,
            ps.lat,
            ps.lng,
            ps.road_addr,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS review_avg_score,
            COUNT(r.review_id) AS review_cnt,
            ps.thumbnail_url,
            GROUP_CONCAT(DISTINCT c.name) AS category_list
        FROM photo_studios ps
        INNER JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
        INNER JOIN category c ON psc.category_id = c.category_id
        LEFT JOIN review r ON r.ps_id = ps.ps_id
        WHERE c.name = :category
          AND CAST(ps.lat AS FLOAT) BETWEEN :sw_lat AND :ne_lat
          AND CAST(ps.lng AS FLOAT) BETWEEN :sw_lng AND :ne_lng
        GROUP BY ps.ps_id
        """)

        params = {
            "sw_lat": sw_lat,
            "ne_lat": ne_lat,
            "sw_lng": sw_lng,
            "ne_lng": ne_lng,
            "category": category,
        }
    else:
        sql = text("""
        SELECT
            ps.ps_id AS id,
            ps.ps_name AS name,
            ps.lat,
            ps.lng,
            ps.road_addr,
            COALESCE(ROUND(AVG(r.rating), 1), 0) AS review_avg_score,
            COUNT(r.review_id) AS review_cnt,
            ps.thumbnail_url,
            GROUP_CONCAT(DISTINCT c.name) AS category_list
        FROM photo_studios ps
        LEFT JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
        LEFT JOIN category c ON psc.category_id = c.category_id
        LEFT JOIN review r ON ps.ps_id = r.ps_id
        WHERE CAST(ps.lat AS FLOAT) BETWEEN :sw_lat AND :ne_lat
          AND CAST(ps.lng AS FLOAT) BETWEEN :sw_lng AND :ne_lng
        GROUP BY ps.ps_id
        """)
        params = {
            "sw_lat": sw_lat,
            "ne_lat": ne_lat,
            "sw_lng": sw_lng,
            "ne_lng": ne_lng,
        }

    rows = db.execute(sql, params).mappings().all()

    markers = []

    for row in rows:
        row_dict = dict(row)  # RowMapping → dict로 변환
        thumbnail = row_dict.get("thumbnail_url")

        if thumbnail:
            row_dict["thumbnail_url"] = get_full_azure_url(thumbnail) if thumbnail else None

        raw = row_dict.get("category_list") or ""
        tags = [f"#{name.strip()}" for name in raw.split(",") if name.strip()]
        row_dict["categories"] = tags

        row_dict.pop("category_list", None)
        markers.append(row_dict)

    return {
        "level": "marker",
        "markers": markers
    }