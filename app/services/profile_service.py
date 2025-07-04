from zoneinfo import ZoneInfo

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth.hash import verify_password, hash_password
from app.dto.response.ReviewResponseSchemas import MyReviewResponse, ReviewPage
from app.models import User, Review, kst_now
from app.util.azure_upload import get_full_azure_url, validate_image_upload, upload_file_to_azure

def verify_user(db, user_info):
    user = db.query(User).filter(User.email == user_info["email"]).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다.")

    return user

def update_profile_image(db: Session, user, file = UploadFile):
    user = verify_user(db, user)

    if not file:
        raise HTTPException(status_code=400, detail="이미지 파일이 필요합니다.")

    try:
        # 파일 검증
        validate_image_upload(file)

        # Azure 업로드
        filename = upload_file_to_azure(file)
        full_image_url = get_full_azure_url(filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail="이미지 업로드 실패: " + str(e))

    # DB에 저장
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    db_user.profile_image = filename
    db.commit()

    return {"message": "프로필 이미지가 업데이트되었습니다.", "profile_image": full_image_url}


def my_recent_reviews(db: Session, user_info, limit = int):
    user = verify_user(db, user_info)

    reviews = (
        db.query(Review)
        .options(joinedload(Review.studio))
        .filter(Review.user_id == user.user_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )

    result: list[MyReviewResponse] = []
    for r in reviews:
        image_url = get_full_azure_url(r.image_url) if r.image_url else None
        result.append(
            MyReviewResponse(
                review_id= r.review_id,
                rating= r.rating,
                content= r.content,
                image_url= image_url,
                ps_id= r.ps_id,
                name= r.studio.ps_name,
                created_at= r.created_at,
                updated_at= r.updated_at,
            )
        )

    return result


def my_review_management(db, user_info, page, size):
    user = verify_user(db, user_info)

    total = db.query(func.count(Review.review_id)) \
            .filter(Review.user_id == user.user_id) \
            .scalar()

    offset = (page - 1) * size
    reviews = (
        db.query(Review)
        .options(joinedload(Review.studio))
        .filter(Review.user_id == user.user_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    items: list[MyReviewResponse] = []
    for r in reviews:
        items.append(
            MyReviewResponse(
                review_id = r.review_id,
                rating= r.rating,
                content= r.content,
                image_url= get_full_azure_url(r.image_url) if r.image_url else None,
                name= r.studio.ps_name,
                ps_id= r.studio.ps_id,
                created_at= r.created_at,
                updated_at= r.updated_at,
            )
        )

    return ReviewPage(
         total= total,
         page= page,
         size= size,
         has_more= (page * size) < total,
         items= items
    )


def delete_my_review(review_id, db, user_info):
    user = verify_user(db, user_info)

    review = db.query(Review).filter(Review.review_id == review_id).first()
    if not review:
        raise HTTPException(404, "리뷰를 찾을 수 없습니다.")

    if review.user_id != user.user_id:
        raise HTTPException(403, "본인이 작성한 리뷰만 삭제할 수 있습니다.")

    db.delete(review)
    db.commit()

    return


def get_current_profile_me(db, user_info):
    user = verify_user(db, user_info)

    return {"message": "인증 성공", "user": {
        "email": user.email,
        "nickname": user.nick_name,
        "profile_image": (
            get_full_azure_url(user.profile_image)
            if user.profile_image else None
        )
    }}


def update_profile_nickname(payload, db, user_info):
    user = verify_user(db, user_info)

    new_nickname = payload.nickname

    exists = (
        db.query(User)
        .filter(user.nick_name == new_nickname, User.user_id != user.user_id)
        .first()
    )

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 닉네임입니다."
        )

    user.nick_name = new_nickname
    db.commit()

    return {"message": "닉네임이 성공적으로 변경되었습니다."}


def verify_current_password(current_password, db, user_info):
    user = verify_user(db, user_info)

    if not verify_password(current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )

    user.recent_password_verified_at = kst_now()
    now = kst_now()
    print(now.tzinfo)
    db.commit()

    return {"message": "비밀번호가 확인되었습니다."}


def change_password(payload, db, user_info):
    user = verify_user(db, user_info)

    verified_at = user.recent_password_verified_at
    if not verified_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="최근 비밀번호 인증이 필요합니다."
        )

    # tzInfo가 없으면 직접 보정
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=ZoneInfo("Asia/Seoul"))

    if (kst_now() - verified_at).total_seconds() > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="최근 비밀번호 인증이 필요합니다."
        )

    if payload.new_password != payload.new_password_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호와 확인이 일치하지 않습니다."
        )

    user.password = hash_password(payload.new_password)
    user.recent_password_verified_at = None # 인증 후 시간 초기화
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}