import time
from threading import Lock


class DangerRuntime:
    def __init__(self):
        self._lock = Lock()

        self.last_danger_seen_ts = 0.0

        self.last_danger_feed_value = None
        self.last_pump_feed_value = None

        self.last_danger_feed_publish_ts = 0.0
        self.last_pump_feed_publish_ts = 0.0

    def compute_pump_command(self, is_danger: bool, safe_hold_seconds: float = 10.0) -> int:
        now = time.time()

        with self._lock:
            if is_danger:
                self.last_danger_seen_ts = now
                return 1

            if (now - self.last_danger_seen_ts) <= safe_hold_seconds:
                return 1

            return 0

    def should_publish_danger(self, value: int, refresh_seconds: float = 4.0) -> bool:
        now = time.time()

        with self._lock:
            if self.last_danger_feed_value is None:
                return True

            if value != self.last_danger_feed_value:
                return True

            if (now - self.last_danger_feed_publish_ts) >= refresh_seconds:
                return True

            return False

    def should_publish_pump(self, value: int, refresh_seconds: float = 4.0) -> bool:
        now = time.time()

        with self._lock:
            if self.last_pump_feed_value is None:
                return True

            if value != self.last_pump_feed_value:
                return True

            if (now - self.last_pump_feed_publish_ts) >= refresh_seconds:
                return True

            return False

    def mark_danger_published(self, value: int):
        now = time.time()

        with self._lock:
            self.last_danger_feed_value = value
            self.last_danger_feed_publish_ts = now

    def mark_pump_published(self, value: int):
        now = time.time()

        with self._lock:
            self.last_pump_feed_value = value
            self.last_pump_feed_publish_ts = now

    def snapshot(self):
        with self._lock:
            return {
                "last_danger_seen_ts": self.last_danger_seen_ts,
                "last_danger_feed_value": self.last_danger_feed_value,
                "last_pump_feed_value": self.last_pump_feed_value,
                "last_danger_feed_publish_ts": self.last_danger_feed_publish_ts,
                "last_pump_feed_publish_ts": self.last_pump_feed_publish_ts,
            }


danger_runtime = DangerRuntime()