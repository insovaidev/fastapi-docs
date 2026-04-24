from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.utils.files import StorageFolder, save_upload_bytes

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    type: Annotated[
        StorageFolder,
        Query(description="Target storage folder"),
    ] = StorageFolder.UPLOADS,
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    stored = save_upload_bytes(folder=type, filename=file.filename, content=content)
    stored["content_type"] = file.content_type or "application/octet-stream"

    return {
        "message": "File uploaded successfully",
        "data": stored,
    }
