from fastapi import APIRouter
from pydantic import BaseModel

from ..services.model_alarm import handle_model_result_to_adafruit

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertPayload(BaseModel):
    danger: bool


@router.post("/test-pump")
async def test_pump_alert(payload: AlertPayload):
    fake_result = {
        "danger_detected": payload.danger,
        "detections": [{"label": "fire"}] if payload.danger else [],
    }

    result = handle_model_result_to_adafruit(
        fake_result,
        safe_hold_seconds=10.0,
        refresh_seconds=4.0,
    )

    return {
        "message": "Pump hold logic tested",
        "danger": result["danger"],
        "danger_feed_value": result["danger_feed_value"],
        "pump_feed_value": result["pump_feed_value"],
        "pump_command_sent": result["pump_command"],
        "runtime": result["runtime"],
        "adafruit": result["adafruit"],
    }