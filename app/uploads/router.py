from fastapi import APIRouter, UploadFile

from app.service.file_storage import save_uploaded_file

router = APIRouter(prefix="/upload", tags=["uploads"])

MEDIA_DIR = "app/media"


@router.post("/save")
async def save_file(file: UploadFile):
    saved = save_uploaded_file(file)

    return {"filename": saved["filename"], "content_type": saved["content_type"], "url": saved["filename"]}
