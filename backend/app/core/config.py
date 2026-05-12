import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "model" / "best.pt"
OUTPUT_DIR = BASE_DIR / "outputs"


class Settings:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "yolohome")

        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "change-me")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        )
        self.sensor_ttl_seconds = int(os.getenv("SENSOR_TTL_SECONDS", "2592000"))

        self.adafruit_io_username = os.getenv("ADAFRUIT_IO_USERNAME", "")
        self.adafruit_io_key = os.getenv("ADAFRUIT_IO_KEY", "")

        self.adafruit_io_temp_feed_key = os.getenv(
            "ADAFRUIT_IO_TEMP_FEED_KEY",
            "bbc-temp",
        )
        self.adafruit_io_humidity_feed_key = os.getenv(
            "ADAFRUIT_IO_HUMIDITY_FEED_KEY",
            "bbc-humidity",
        )
        self.adafruit_io_brightness_feed_key = os.getenv(
            "ADAFRUIT_IO_BRIGHTNESS_FEED_KEY",
            "bbc-brightness",
        )

        self.adafruit_io_danger_feed_key = os.getenv(
            "ADAFRUIT_IO_DANGER_FEED_KEY",
            "danger-detected",
        )
        self.adafruit_io_pump_command_feed_key = os.getenv(
            "ADAFRUIT_IO_PUMP_COMMAND_FEED_KEY",
            "pump-command",
        )
        self.adafruit_io_pump_status_feed_key = os.getenv(
            "ADAFRUIT_IO_PUMP_STATUS_FEED_KEY",
            "pump-status",
        )


settings = Settings()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)