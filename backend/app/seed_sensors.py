from datetime import datetime, timedelta, timezone
import random

from pymongo import MongoClient
from app.core.config import settings


def main():
    client = MongoClient(settings.mongo_uri)
    db = client[settings.db_name]

    now = datetime.now(timezone.utc)

    docs = []
    for i in range(20):
        docs.append(
            {
                "timestamp": now - timedelta(minutes=i * 5),
                "metadata": {
                    "device_id": "esp32",
                },
                "temperature": round(random.uniform(40, 60), 1),
                "humidity": round(random.uniform(55, 80), 1),
                "gas": random.randint(120, 300),
                "light": random.randint(200, 650),
                "flame": random.choice([0, 0, 0, 1]),
                "relay_status": random.choice([True, False]),
                "buzzer_status": random.choice([True, False]),
                "led_status": random.choice([True, False]),
            }
        )

    result = db.sensor_readings.insert_many(docs)
    print("Inserted sensor docs:", len(result.inserted_ids))

    client.close()


if __name__ == "__main__":
    main()