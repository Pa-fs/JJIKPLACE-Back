from sqlalchemy import text
from sqlalchemy.orm import Session


def get_review_details_in_photo_studio(db: Session, ps_id: int, offset: int, limit: int):
    try:
        sql = text("""
        SELECT
            r.review_id,
            r.rating,
            r.content,
            r.created_at,
            u.nick_name AS user_nickname
        FROM review r
        INNER JOIN user u ON r.user_id = u.user_id
        WHERE r.ps_id = :ps_id
        ORDER BY r.created_at DESC
        LIMIT :limit OFFSET :offset
        """)

        result = db.execute(sql, {
            "ps_id": ps_id,
            "limit": limit,
            "offset": offset
        }).mappings().all()

        count_sql = text("SELECT COUNT(*) FROM review WHERE ps_id = :ps_id")
        total = db.execute(count_sql, {"ps_id": ps_id}).scalar()

        return {
            "items": result,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(result) < total
        }
    except Exception as e:
        print(f"리뷰 목록 조회 시 에러 발생: {e}")
        return []