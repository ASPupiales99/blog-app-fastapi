import os
import shutil
import uuid

from fastapi import File, UploadFile, HTTPException, status

MEDIA_DIR = "app/media"
ALLOW_MIME = ["image/jpeg", "image/png"]
MAX_MB = int(os.environ.get("MAX_MB", "10"))
CHUNKS = 1024 * 1024


def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)


def save_uploaded_file(file: UploadFile = File(...)) -> dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid file type, pleas use png or jpg images")

    ensure_media_dir()
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(MEDIA_DIR, filename)
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f, length=CHUNKS)

    size = os.path.getsize(file_path)
    if size > MAX_MB * CHUNKS:
        os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=f"File too large (> {MAX_MB} MB)")

    return {"filename": filename, "content_type": file.content_type, "url": f"/media/{filename}"}
