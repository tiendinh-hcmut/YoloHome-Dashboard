from datetime import datetime, timezone
from fastapi import APIRouter, File, UploadFile, Depends

from ..core.database import get_db
from ..services.yolo_service import (
    MODEL_NAME,
    MODEL_VERSION,
    detect_frame_bytes,
    detect_image_bytes,
    detect_video_file,
)

router = APIRouter(prefix="/api", tags=["model"])


@router.get("/health")
async def health(db=Depends(get_db)):
    db_status = "disconnected"

    try:
        ping = await db.command("ping")
        if int(ping["ok"]) == 1:
            db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "backend": "running",
        "database": db_status,
        "model_loaded": True,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    content = await file.read()
    return detect_image_bytes(content)


@router.post("/detect-frame")
async def detect_frame(file: UploadFile = File(...)):
    content = await file.read()
    return detect_frame_bytes(content)


@router.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    return detect_video_file(file.file, file.filename)
