from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import ASCENDING, AsyncMongoClient
from .config import settings

mongodb_client: AsyncMongoClient | None = None
database = None


async def init_db():
    global database

    existing = await database.list_collection_names()

    if "sensor_readings" not in existing:
        await database.create_collection(
            "sensor_readings",
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "seconds",
            },
            expireAfterSeconds=settings.sensor_ttl_seconds,
        )

    await database.users.create_index([("username", ASCENDING)], unique=True)
    await database.users.create_index([("email", ASCENDING)], unique=True)
    await database.users.create_index([("role", ASCENDING)])


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb_client, database

    mongodb_client = AsyncMongoClient(settings.mongo_uri)
    database = mongodb_client[settings.db_name]

    await database.command("ping")
    await init_db()

    app.state.mongodb_client = mongodb_client
    app.state.database = database
    yield

    if mongodb_client is not None:
        mongodb_client.close()


def get_db():
    if database is None:
        raise RuntimeError("Database is not initialized")
    return database
