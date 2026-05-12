from app.services.adafruit_io import publish_danger_state, publish_pump_command
from app.services.danger_runtime import danger_runtime


DANGER_LABELS = {"danger", "fire", "smoke"}


def _normalize_text(value):
    return str(value or "").strip().lower()


def _dict_says_danger(item: dict) -> bool:
    if not isinstance(item, dict):
        return False

    for key in (
        "danger_detected",
        "alert_triggered",
        "is_danger",
        "has_danger",
        "danger",
    ):
        if bool(item.get(key)):
            return True

    for key in ("main_label", "label", "class_name", "name"):
        if _normalize_text(item.get(key)) in DANGER_LABELS:
            return True

    detections = item.get("detections") or []
    for det in detections:
        if isinstance(det, dict):
            for key in ("label", "class_name", "name"):
                if _normalize_text(det.get(key)) in DANGER_LABELS:
                    return True

            for key in ("danger_detected", "alert_triggered", "is_danger", "has_danger"):
                if bool(det.get(key)):
                    return True

    items = item.get("items") or item.get("results") or item.get("frames") or []
    for sub in items:
        if isinstance(sub, dict) and _dict_says_danger(sub):
            return True

    return False


def is_danger_result(result) -> bool:
    if result is None:
        return False

    if isinstance(result, dict):
        return _dict_says_danger(result)

    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and _dict_says_danger(item):
                return True
        return False

    return False


def handle_model_result_to_adafruit(
    result,
    safe_hold_seconds: float = 10.0,
    refresh_seconds: float = 4.0,
):
    is_danger = is_danger_result(result)
    pump_command = danger_runtime.compute_pump_command(
        is_danger=is_danger,
        safe_hold_seconds=safe_hold_seconds,
    )

    danger_publish_result = None
    pump_publish_result = None

    danger_value = 1 if is_danger else 0
    pump_value = 1 if bool(pump_command) else 0

    if danger_runtime.should_publish_danger(danger_value, refresh_seconds=refresh_seconds):
        danger_publish_result = publish_danger_state(bool(danger_value))
        danger_runtime.mark_danger_published(danger_value)
    else:
        print(f"[ADAFRUIT] skip publish danger-detected={danger_value}")

    if danger_runtime.should_publish_pump(pump_value, refresh_seconds=refresh_seconds):
        pump_publish_result = publish_pump_command(bool(pump_value))
        danger_runtime.mark_pump_published(pump_value)
    else:
        print(f"[ADAFRUIT] skip publish pump-command={pump_value}")

    return {
        "danger": is_danger,
        "pump_command": pump_command,
        "danger_feed_value": danger_value,
        "pump_feed_value": pump_value,
        "adafruit": {
            "danger_feed": danger_publish_result,
            "pump_command_feed": pump_publish_result,
        },
        "runtime": danger_runtime.snapshot(),
    }