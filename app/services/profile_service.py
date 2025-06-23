from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import User
from app.util.azure_upload import get_full_azure_url, validate_image_upload, upload_file_to_azure


def update_profile_image(db: Session, user, file = UploadFile):
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
    db_user = db.query(User).filter(User.email == user["email"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    db_user.profile_image = filename
    db.commit()

    return {"message": "프로필 이미지가 업데이트되었습니다.", "profile_image": full_image_url}