import time
from datetime import datetime, timezone
from threading import Event

import requests
from pymongo import MongoClient

from app.core.config import settings


def parse_datetime(value: str):
    if not value:
        return datetime.now(timezone.utc)

    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def parse_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_last_feed_data(feed_key: str):
    url = f"https://io.adafruit.com/api/v2/{settings.adafruit_io_username}/feeds/{feed_key}/data/last"

    headers = {
        "X-AIO-Key": settings.adafruit_io_key.strip(),
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def build_sync_signature(temp_data, humidity_data, brightness_data):
    temp_id = temp_data.get("id", "")
    humidity_id = humidity_data.get("id", "")
    brightness_id = brightness_data.get("id", "")
    return f"{temp_id}|{humidity_id}|{brightness_id}"


def get_latest_timestamp(*items):
    timestamps = []

    for item in items:
        created_at = item.get("created_at")
        if created_at:
            timestamps.append(parse_datetime(created_at))

    if not timestamps:
        return datetime.now(timezone.utc)

    return max(timestamps)


def save_combined_sensor_reading_if_new(temp_data, humidity_data, brightness_data):
    client = MongoClient(settings.mongo_uri)
    db = client[settings.db_name]

    try:
        signature = build_sync_signature(temp_data, humidity_data, brightness_data)

        state = db.sync_state.find_one({"source": "adafruit-bbc-multi"})
        if state and state.get("last_signature") == signature:
            print("No new Adafruit data, skip insert")
            return

        temperature = parse_number(temp_data.get("value"))
        humidity = parse_number(humidity_data.get("value"))
        light = parse_number(brightness_data.get("value"))

        sensor_doc = {
            "timestamp": get_latest_timestamp(temp_data, humidity_data, brightness_data),
            "metadata": {
                "device_id": "esp32",
                "provider": "adafruit-io",
                "username": settings.adafruit_io_username,
            },
            "temperature": temperature,
            "humidity": humidity,
            "light": light,
            "gas": None,
            "flame": None,
            "relay_status": False,
            "buzzer_status": False,
            "led_status": False,
            "source": "adafruit-io-realtime",
            "feed_map": {
                "temperature": settings.adafruit_io_temp_feed_key,
                "humidity": settings.adafruit_io_humidity_feed_key,
                "light": settings.adafruit_io_brightness_feed_key,
            },
            "adafruit_ids": {
                "temperature": temp_data.get("id"),
                "humidity": humidity_data.get("id"),
                "light": brightness_data.get("id"),
            },
            "raw_values": {
                "temperature": temp_data.get("value"),
                "humidity": humidity_data.get("value"),
                "light": brightness_data.get("value"),
            },
            "created_at_adafruit": {
                "temperature": temp_data.get("created_at"),
                "humidity": humidity_data.get("created_at"),
                "light": brightness_data.get("created_at"),
            },
        }

        sensor_doc = {k: v for k, v in sensor_doc.items() if v is not None}

        db.sensor_readings.insert_one(sensor_doc)

        db.sync_state.update_one(
            {"source": "adafruit-bbc-multi"},
            {
                "$set": {
                    "last_signature": signature,
                    "last_synced_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )

        print("Inserted new combined Adafruit reading:")
        print(
            {
                "device_id": sensor_doc["metadata"]["device_id"],
                "temperature": sensor_doc.get("temperature"),
                "humidity": sensor_doc.get("humidity"),
                "light": sensor_doc.get("light"),
                "timestamp": sensor_doc.get("timestamp"),
            }
        )
    finally:
        client.close()


def sync_once():
    temp_data = fetch_last_feed_data(settings.adafruit_io_temp_feed_key)
    humidity_data = fetch_last_feed_data(settings.adafruit_io_humidity_feed_key)
    brightness_data = fetch_last_feed_data(settings.adafruit_io_brightness_feed_key)

    save_combined_sensor_reading_if_new(
        temp_data,
        humidity_data,
        brightness_data,
    )


def run_sync_loop(stop_event: Event | None = None, interval_seconds: int = 10):
    print(f"Starting Adafruit multi-feed realtime sync every {interval_seconds} seconds...")

    while True:
        if stop_event and stop_event.is_set():
            print("Stopping Adafruit sync loop")
            break

        try:
            sync_once()
        except Exception as exc:
            print("Sync error:", exc)

        if stop_event:
            if stop_event.wait(interval_seconds):
                print("Stopping Adafruit sync loop")
                break
        else:
            time.sleep(interval_seconds)


def main():
    run_sync_loop(interval_seconds=10)


if __name__ == "__main__":
    main()