from sqlalchemy import text
from sqlalchemy.orm import Session


def get_nearby_studios(db: Session, lat: float, lng: float, offset: int, limit: int, category: str = None):
    # 거리 계산: Haversine Formula (km 단위)
    sql = """
    SELECT
        ps.ps_id,
        ps.ps_name AS name,
        ps.lat,
        ps.lng,
        ps.road_addr,
        COALESCE(ROUND(AVG(r.rating), 1), 0) AS review_avg_score,
        COUNT(r.review_id) AS review_cnt,
        ROUND(
            6371 * acos(
                cos(radians(:lat)) * cos(radians(CAST(ps.lat AS DOUBLE)))
              * cos(radians(CAST(ps.lng AS DOUBLE)) - radians(:lng))
              + sin(radians(:lat)) * sin(radians(CAST(ps.lat AS DOUBLE)))
            ),
            2
        ) AS distance_km
    FROM photo_studios ps
    LEFT JOIN review r ON ps.ps_id = r.ps_id
    {category_join}
    WHERE ps.lat IS NOT NULL AND ps.lng IS NOT NULL
    {category_filter}
    GROUP BY ps.ps_id
    HAVING distance_km <= 5
    ORDER BY distance_km ASC
    LIMIT :limit OFFSET :offset
    """
    count_sql = """
        SELECT COUNT(*) FROM (
            SELECT
                ps.ps_id,
                ROUND(
                    6371 * acos(
                        cos(radians(:lat)) * cos(radians(CAST(ps.lat AS DOUBLE)))
                      * cos(radians(CAST(ps.lng AS DOUBLE)) - radians(:lng))
                      + sin(radians(:lat)) * sin(radians(CAST(ps.lat AS DOUBLE)))
                    ),
                    2
                ) AS distance_km
            FROM photo_studios ps
            {category_join}
            WHERE ps.lat IS NOT NULL 
              AND ps.lng IS NOT NULL
            {category_filter}
            GROUP BY ps.ps_id
            HAVING distance_km <= 5
        ) AS filtered
    """

    if category:
        category_join = """
        INNER JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
        INNER JOIN category c ON psc.category_id = c.category_id
        """
        category_filter = "AND c.name = :category"
    else:
        category_join = ""
        category_filter = ""

    sql = sql.format(category_join=category_join, category_filter=category_filter)
    count_sql = count_sql.format(category_join=category_join, category_filter=category_filter)

    params = {"lat": lat, "lng": lng, "offset": offset, "limit": limit}

    if category:
        params["category"] = category

    result = db.execute(text(sql), params).mappings().all()
    total = db.execute(text(count_sql), params).scalar()

    return result, total