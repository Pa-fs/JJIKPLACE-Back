from sqlalchemy import text
from sqlalchemy.orm import Session

from app.util.azure_upload import get_full_azure_url


def get_nearby_studios(db: Session, lat: float, lng: float, offset: int, limit: int, category: str = None):
    # 거리 계산: Haversine Formula (km 단위)
    # 공통 SELECT 절 (distance_km 포함)
    distance_expr = """
        ROUND(
            6371 * acos(
                cos(radians(:lat)) * cos(radians(CAST(ps.lat AS DOUBLE)))
              * cos(radians(CAST(ps.lng AS DOUBLE)) - radians(:lng))
              + sin(radians(:lat)) * sin(radians(CAST(ps.lat AS DOUBLE)))
            ),
            2
        ) AS distance_km
    """

    # 메인 쿼리
    sql = f"""
    SELECT
      ps.ps_id,
      ps.ps_name AS name,
      ps.lat,
      ps.lng,
      ps.road_addr,
      COALESCE(ROUND(AVG(r.rating), 1), 0) AS review_avg_score,
      COUNT(r.review_id) AS review_cnt,
      {distance_expr},
      ps.thumbnail_url,
      GROUP_CONCAT(DISTINCT c.name) AS category_list
    FROM photo_studios ps
    LEFT JOIN review r ON ps.ps_id = r.ps_id
    LEFT JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
    LEFT JOIN category c ON psc.category_id = c.category_id
    WHERE ps.lat IS NOT NULL
      AND ps.lng IS NOT NULL
      { 'AND c.name = :category' if category else '' }
    GROUP BY ps.ps_id
    HAVING distance_km <= 5
    ORDER BY distance_km ASC
    LIMIT :limit OFFSET :offset
    """

    # 카운트용 쿼리: distance_km 포함
    count_sql = f"""
    SELECT COUNT(*) FROM (
      SELECT
        ps.ps_id,
        {distance_expr}
      FROM photo_studios ps
      LEFT JOIN photo_studio_category psc ON ps.ps_id = psc.ps_id
      LEFT JOIN category c ON psc.category_id = c.category_id
      WHERE ps.lat IS NOT NULL
        AND ps.lng IS NOT NULL
        { 'AND c.name = :category' if category else '' }
      GROUP BY ps.ps_id
      HAVING distance_km <= 5
    ) AS filtered
    """

    params = {"lat": lat, "lng": lng, "offset": offset, "limit": limit}
    if category:
        params["category"] = category

    rows = db.execute(text(sql), params).mappings().all()
    total = db.execute(text(count_sql), params).scalar() or 0

    items = []
    for row in rows:
        d = dict(row)
        # 썸네일 URL
        thumb = d.get("thumbnail_url")
        d["thumbnail_url"] = get_full_azure_url(thumb) if thumb else None

        # 카테고리 해시태그 변환
        raw = d.get("category_list") or ""
        d["categories"] = [f"#{name.strip()}" for name in raw.split(",") if name.strip()]

        # 더 이상 필요 없는 필드 삭제
        d.pop("category_list", None)

        items.append(d)

    has_more = (offset + len(items)) < total

    return items, total, has_more