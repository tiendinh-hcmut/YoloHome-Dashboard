from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import get_current_user

router = APIRouter(prefix="/api/devices", tags=["devices"])


class DeviceControlPayload(BaseModel):
    device_id: str
    led: bool | None = None
    relay: bool | None = None
    buzzer: bool | None = None


@router.post("/control")
async def control_devices(
    payload: DeviceControlPayload,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    update_doc = {
        "device_id": payload.device_id,
        "updated_at": datetime.now(timezone.utc),
    }

    if payload.led is not None:
        update_doc["led"] = payload.led
    if payload.relay is not None:
        update_doc["relay"] = payload.relay
    if payload.buzzer is not None:
        update_doc["buzzer"] = payload.buzzer

    await db.device_states.update_one(
        {"device_id": payload.device_id},
        {"$set": update_doc},
        upsert=True,
    )

    doc = await db.device_states.find_one({"device_id": payload.device_id})

    return {
        "message": "Device control updated",
        "device_id": doc["device_id"],
        "led": doc.get("led", False),
        "relay": doc.get("relay", False),
        "buzzer": doc.get("buzzer", False),
        "updated_at": doc.get("updated_at"),
    }


@router.get("/status")
async def get_device_status(
    device_id: str = Query(...),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    doc = await db.device_states.find_one({"device_id": device_id})

    if not doc:
        return {
            "device_id": device_id,
            "led": False,
            "relay": False,
            "buzzer": False,
            "updated_at": None,
        }

    return {
        "device_id": doc["device_id"],
        "led": doc.get("led", False),
        "relay": doc.get("relay", False),
        "buzzer": doc.get("buzzer", False),
        "updated_at": doc.get("updated_at"),
    }