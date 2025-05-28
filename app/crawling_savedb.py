from sqlalchemy.orm import Session

from app.crawler import extract_place_details
from app.models import PhotoStudio, Review


def save_studio_and_reviews(db: Session, studio_data: dict, place_id: str):

    detail = extract_place_details(f"https://place.map.kakao.com/{place_id}")
    print(f"detail: {detail}")

    studio_data["open_hour"] = detail["open_hour"]
    studio_data["homepage_url"] = detail["homepage"]

    # 스튜디오 저장 (Upsert용: kakao_id 기준)
    studio = db.query(PhotoStudio).filter_by(kakao_id=studio_data["kakao_id"]).first()
    if not studio:
        studio = PhotoStudio(**studio_data)
        db.add(studio)
    else:
        for k, v in studio_data.items():
            setattr(studio, k, v)
        print("업데이트 중:", studio.kakao_id, studio.open_hour, studio.homepage_url)
    db.commit()
    db.refresh(studio)

    # 후기 저장 (유저 정보 없으므로 user_id 임시로 1 설정)
    for review in detail["reviews"]:
        print("리뷰 저장:", review["content"], "/", review.get("rating"))

        new_review = Review(
            rating = review.get("rating", None),
            content = review.get("content", None),
            image_url = None,
            created_at = review.get("date", None),
            ps_id = studio.ps_id,
            user_id = 1
        )
        db.add(new_review)
    db.commit()