import requests

from app.core.config import settings


def publish_feed_value(feed_key: str, value):
    if not settings.adafruit_io_username or not settings.adafruit_io_key:
        raise RuntimeError("Missing ADAFRUIT_IO_USERNAME or ADAFRUIT_IO_KEY")

    url = f"https://io.adafruit.com/api/v2/{settings.adafruit_io_username}/feeds/{feed_key}/data"
    headers = {
        "X-AIO-Key": settings.adafruit_io_key.strip(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(
        url,
        headers=headers,
        json={"value": value},
        timeout=15,
    )
    response.raise_for_status()

    print(f"[ADAFRUIT] feed='{feed_key}' value='{value}' -> OK")
    return response.json()


def publish_danger_state(is_danger: bool):
    return publish_feed_value(
        settings.adafruit_io_danger_feed_key,
        1 if is_danger else 0,
    )


def publish_pump_command(is_on: bool):
    return publish_feed_value(
        settings.adafruit_io_pump_command_feed_key,
        1 if is_on else 0,
    )