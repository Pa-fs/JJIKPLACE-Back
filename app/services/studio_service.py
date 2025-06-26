from datetime import timedelta

from sqlalchemy import func, literal

from app.dto.response.StudioResponseSchemas import RankedStudio
from app.models import kst_now, Review, PhotoStudio


def get_studio_ranking(db, days, m, limit):
    """
    WR = (v / (v + m)) * R + (m / (v + m)) * C
        R : 스튜디오 평균 평점
        v : 스튜디오 리뷰 수
        m : 기준 리뷰 수
        C : 전체 평균 평점
    """

    since = kst_now() - timedelta(days=days)

    C = (
        db.query(func.avg(Review.rating))
        .filter(Review.created_at >= since)
        .scalar()
    ) or 0

    subq = (
        db.query(
            Review.ps_id.label("ps_id"),
            func.count(Review.review_id).label("v"),
            func.avg(Review.rating).label("R"),
        )
        .filter(Review.created_at >= since)
        .group_by(Review.ps_id)
        .subquery()
    )

    # WR 계산
    wr_expr = (
        (subq.c.v / (subq.c.v + literal(m))) * subq.c.R +
         (literal(m) / (subq.c.v + literal(m))) * C
    ).label("wr")

    studios = (
        db.query(
            PhotoStudio.ps_id,
            PhotoStudio.ps_name,
            subq.c.R,
            subq.c.v,
            wr_expr
        )
        .join(subq, PhotoStudio.ps_id == subq.c.ps_id)
        .filter(subq.c.v >= m) # 최소 리뷰 수 m개 이상
        .order_by(wr_expr.desc(), subq.c.v.desc())
        .limit(limit)
        .all()
    )

    result: list[RankedStudio] = []
    for idx, s in enumerate(studios, start= 1):
        result.append(
            RankedStudio(
            rank= idx,
            ps_id= s.ps_id,
            name= s.ps_name,
            avg_rating= round(s.R, 2),
            review_cnt= int(s.v),
            weighted_rating= round(s.wr, 3),
            image_url= None
        )
    )

    return result