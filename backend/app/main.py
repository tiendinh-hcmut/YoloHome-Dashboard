from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.alerts import router as alerts_router
from .api.auth import router as auth_router
from .api.devices import router as devices_router
from .api.model import router as model_router
from .api.sensors import router as sensors_router
from .core.adafruit_runner import start_adafruit_sync, stop_adafruit_sync
from .core.config import OUTPUT_DIR
from .core.database import lifespan as database_lifespan


async def app_lifespan(app: FastAPI):
    async with database_lifespan(app):
        start_adafruit_sync()
        yield
        stop_adafruit_sync()


app = FastAPI(
    title="YOLOHome API",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

app.include_router(auth_router)
app.include_router(model_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(alerts_router)