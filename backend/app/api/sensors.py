from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.database import get_db
from ..core.security import get_current_user
from ..schemas import SensorIngest

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.post("/data")
async def ingest_sensor_data(payload: SensorIngest, db=Depends(get_db)):
    ts = payload.timestamp or datetime.now(timezone.utc)

    doc = {
        "timestamp": ts,
        "metadata": {
            "device_id": payload.device_id,
        },
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "gas": payload.gas,
        "light": payload.light,
        "flame": payload.flame,
        "relay_status": payload.relay_status,
        "buzzer_status": payload.buzzer_status,
        "led_status": payload.led_status,
    }

    doc = {k: v for k, v in doc.items() if v is not None}

    result = await db.sensor_readings.insert_one(doc)

    return {
        "message": "Sensor data saved",
        "id": str(result.inserted_id),
        "timestamp": ts,
    }


@router.get("/latest")
async def get_latest_sensor(
    device_id: str | None = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    query = {}
    if device_id:
        query["metadata.device_id"] = device_id

    doc = await db.sensor_readings.find_one(query, sort=[("timestamp", -1)])

    if not doc:
        raise HTTPException(status_code=404, detail="No sensor data found")

    return {
        "id": str(doc["_id"]),
        "device_id": doc["metadata"]["device_id"],
        "temperature": doc.get("temperature"),
        "humidity": doc.get("humidity"),
        "gas": doc.get("gas"),
        "light": doc.get("light"),
        "flame": doc.get("flame"),
        "relay_status": doc.get("relay_status"),
        "buzzer_status": doc.get("buzzer_status"),
        "led_status": doc.get("led_status"),
        "timestamp": doc["timestamp"],
    }


@router.get("/history")
async def get_sensor_history(
    limit: int = Query(default=50, ge=1, le=500),
    device_id: str | None = None,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    query = {}
    if device_id:
        query["metadata.device_id"] = device_id

    items = []
    async for doc in db.sensor_readings.find(query).sort("timestamp", -1).limit(limit):
        items.append(
            {
                "id": str(doc["_id"]),
                "device_id": doc["metadata"]["device_id"],
                "temperature": doc.get("temperature"),
                "humidity": doc.get("humidity"),
                "gas": doc.get("gas"),
                "light": doc.get("light"),
                "flame": doc.get("flame"),
                "relay_status": doc.get("relay_status"),
                "buzzer_status": doc.get("buzzer_status"),
                "led_status": doc.get("led_status"),
                "timestamp": doc["timestamp"],
            }
        )

    return {"items": items, "count": len(items)}
