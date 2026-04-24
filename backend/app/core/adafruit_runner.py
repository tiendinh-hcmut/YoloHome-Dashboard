from threading import Event, Thread

from app.sync_adafruit_realtime import run_sync_loop

_sync_thread: Thread | None = None
_stop_event: Event | None = None


def start_adafruit_sync():
    global _sync_thread, _stop_event

    if _sync_thread and _sync_thread.is_alive():
        print("Adafruit sync already running")
        return

    _stop_event = Event()
    _sync_thread = Thread(
        target=run_sync_loop,
        kwargs={
            "stop_event": _stop_event,
            "interval_seconds": 5,
        },
        daemon=True,
        name="adafruit-sync-thread",
    )
    _sync_thread.start()
    print("Adafruit sync thread started")


def stop_adafruit_sync():
    global _sync_thread, _stop_event

    if _stop_event:
        _stop_event.set()

    if _sync_thread and _sync_thread.is_alive():
        _sync_thread.join(timeout=3)

    _sync_thread = None
    _stop_event = None
    print("Adafruit sync thread stopped")