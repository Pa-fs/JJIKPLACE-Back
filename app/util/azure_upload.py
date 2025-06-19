import os
import uuid

from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import UploadFile

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_PUBLIC_URL = os.getenv("AZURE_STORAGE_PUBLIC_URL")

ALLOWED_EXTENSIONS = os.getenv("ALLOWED_FILE_EXTENSIONS")
MAX_FILE_SIZE_MB = os.getenv("MAX_FILE_SIZE_MB")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

def upload_file_to_azure(file: UploadFile) -> str:
    """
    파일을 Azure Blob Storage에 업로드하고 파일명을 반환한다 (uuid + 원본 파일명)
    """
    # 예: original name → selfie.jpg → 83f1a2e2-selfie.jpg
    unique_filename = f"{uuid.uuid4()}-{file.filename}"

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=unique_filename
    )

    blob_client.upload_blob(
        file.file,
        overwrite=True,
        content_settings=ContentSettings(content_type=file.content_type)
    )

    return unique_filename

def get_full_azure_url(filename: str) -> str:
    return f"{AZURE_PUBLIC_URL}/{filename}"


def validate_image_upload(file: UploadFile):
    # 확장자 확인
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="허용되지 않은 이미지 확장자입니다.")

    # 파일크기 확인
    contents = file.file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="이미지 크기는 5MB 이하만 허용됩니다.")

    # 파일 포인터 초기화
    file.file.seek(0)
