from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, UploadFile

from ..core.database import get_db
from ..services.model_alarm import handle_model_result_to_adafruit
from ..services.yolo_service import (
    MODEL_NAME,
    MODEL_VERSION,
    detect_frame_bytes,
    detect_image_bytes,
    detect_video_file,
)

router = APIRouter(prefix="/api", tags=["model"])


def attach_adafruit_alarm(result):
    try:
        alarm_result = handle_model_result_to_adafruit(
            result,
            safe_hold_seconds=10.0,
            refresh_seconds=4.0,
        )

        if isinstance(result, dict):
            result["danger_synced"] = alarm_result["danger"]
            result["pump_command_sent"] = alarm_result["pump_command"]
            result["danger_feed_value"] = alarm_result["danger_feed_value"]
            result["pump_feed_value"] = alarm_result["pump_feed_value"]
            result["adafruit_alarm"] = "ok"
            result["danger_runtime"] = alarm_result["runtime"]
            return result

        if isinstance(result, list):
            return {
                "items": result,
                "danger_synced": alarm_result["danger"],
                "pump_command_sent": alarm_result["pump_command"],
                "danger_feed_value": alarm_result["danger_feed_value"],
                "pump_feed_value": alarm_result["pump_feed_value"],
                "adafruit_alarm": "ok",
                "danger_runtime": alarm_result["runtime"],
            }

        return result

    except Exception as exc:
        print("Adafruit publish error:", exc)

        if isinstance(result, dict):
            result["danger_synced"] = False
            result["pump_command_sent"] = 0
            result["danger_feed_value"] = 0
            result["pump_feed_value"] = 0
            result["adafruit_alarm"] = f"error: {exc}"
            return result

        if isinstance(result, list):
            return {
                "items": result,
                "danger_synced": False,
                "pump_command_sent": 0,
                "danger_feed_value": 0,
                "pump_feed_value": 0,
                "adafruit_alarm": f"error: {exc}",
            }

        return result


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
    result = detect_image_bytes(content)
    response = attach_adafruit_alarm(result)
    print(
        f"[IMAGE] danger_synced={response.get('danger_synced')} "
        f"danger_feed_value={response.get('danger_feed_value')} "
        f"pump_feed_value={response.get('pump_feed_value')}"
    )
    return response


@router.post("/detect-frame")
async def detect_frame(file: UploadFile = File(...)):
    content = await file.read()
    print(f"[FRAME] received bytes={len(content)}")
    result = detect_frame_bytes(content)
    response = attach_adafruit_alarm(result)
    print(
        f"[FRAME] danger_synced={response.get('danger_synced')} "
        f"danger_feed_value={response.get('danger_feed_value')} "
        f"pump_feed_value={response.get('pump_feed_value')} "
        f"pump_command_sent={response.get('pump_command_sent')} "
        f"adafruit_alarm={response.get('adafruit_alarm')}"
    )
    return response


@router.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    result = detect_video_file(file.file, file.filename)
    response = attach_adafruit_alarm(result)
    print(
        f"[VIDEO] danger_synced={response.get('danger_synced')} "
        f"danger_feed_value={response.get('danger_feed_value')} "
        f"pump_feed_value={response.get('pump_feed_value')}"
    )
    return response