import cv2
import io
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from PIL import Image
from ultralytics import YOLO

from ..core.config import MODEL_PATH, OUTPUT_DIR

MODEL_NAME = Path(MODEL_PATH).name
MODEL_VERSION = "YOLOv8 custom fire-smoke"

FIRE_THRESHOLD = 0.1
SMOKE_THRESHOLD = 0.1

model = YOLO(str(MODEL_PATH))


def is_danger(label: str, conf: float) -> bool:
    if label == "fire" and conf >= FIRE_THRESHOLD:
        return True
    if label == "smoke" and conf >= SMOKE_THRESHOLD:
        return True
    return False


def parse_result(result):
    detections = []
    danger_detected = False

    names = result.names
    boxes = result.boxes

    if boxes is None:
        return detections, danger_detected

    for box in boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        label = names[cls_id]

        xyxy = box.xyxy[0].tolist()
        x1, y1, x2, y2 = [round(v, 2) for v in xyxy]

        detections.append(
            {
                "label": label,
                "confidence": round(conf, 4),
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                },
            }
        )

        if is_danger(label, conf):
            danger_detected = True

    return detections, danger_detected


def save_annotated_image(result, prefix="frame"):
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.jpg"
    output_path = OUTPUT_DIR / filename
    plotted = result.plot()
    cv2.imwrite(str(output_path), plotted)
    return f"/outputs/{filename}"


def detect_image_bytes(content: bytes):
    image = Image.open(io.BytesIO(content)).convert("RGB")
    results = model(image, conf=0.1, iou=0.7, imgsz=640)
    result = results[0]

    detections, danger_detected = parse_result(result)
    annotated_url = save_annotated_image(result, prefix="image")

    return {
        "message": "Image processed",
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "danger_detected": danger_detected,
        "object_count": len(detections),
        "annotated_image_url": annotated_url,
        "detections": detections,
    }


def detect_frame_bytes(content: bytes):
    image = Image.open(io.BytesIO(content)).convert("RGB")
    results = model(image, conf=0.1, iou=0.7, imgsz=640)
    result = results[0]

    detections, danger_detected = parse_result(result)
    annotated_url = save_annotated_image(result, prefix="frame")

    alarm_action = {
        "buzzer": danger_detected,
        "led": danger_detected,
        "relay": False,
    }

    return {
        "message": "Frame processed",
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "danger_detected": danger_detected,
        "object_count": len(detections),
        "annotated_image_url": annotated_url,
        "alarm_action": alarm_action,
        "detections": detections,
    }


def detect_video_file(file_obj, filename: str | None):
    suffix = os.path.splitext(filename or "video.mp4")[1] or ".mp4"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file_obj, tmp)
        temp_video_path = tmp.name

    cap = cv2.VideoCapture(temp_video_path)

    frame_index = 0
    sample_every = 15
    alert_frames = 0
    max_conf = 0.0
    preview_urls = []
    all_events = []

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame_index += 1
        if frame_index % sample_every != 0:
            continue

        results = model(frame, conf=0.1, iou=0.7, imgsz=640)
        result = results[0]

        detections, danger_detected = parse_result(result)

        if detections:
            max_conf = max(max_conf, max([d["confidence"] for d in detections], default=0.0))

        if danger_detected:
            alert_frames += 1
            preview_url = save_annotated_image(result, prefix="video")

            if len(preview_urls) < 5:
                preview_urls.append(preview_url)

            all_events.append(
                {
                    "frame_index": frame_index,
                    "danger_detected": danger_detected,
                    "detections": detections,
                }
            )

    cap.release()
    os.remove(temp_video_path)

    return {
        "message": "Video processed",
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "danger_detected": alert_frames > 0,
        "alert_frame_count": alert_frames,
        "sampled_events": all_events[:10],
        "preview_images": preview_urls,
        "max_confidence": round(max_conf, 4),
    }
