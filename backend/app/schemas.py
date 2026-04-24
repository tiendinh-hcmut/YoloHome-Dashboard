from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None
    role: Literal["admin", "operator", "viewer"] = "operator"


class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    role: Literal["admin", "operator", "viewer"]
    allowed_dashboards: list[str]
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class SensorIngest(BaseModel):
    device_id: str
    temperature: float | None = None
    humidity: float | None = None
    gas: float | None = None
    light: float | None = None
    flame: float | None = None
    relay_status: bool | None = None
    buzzer_status: bool | None = None
    led_status: bool | None = None
    timestamp: datetime | None = None


def default_dashboards_for_role(role: str) -> list[str]:
    if role == "admin":
        return ["vision", "iot"]
    if role == "operator":
        return ["vision", "iot"]
    return ["vision"]


def user_to_public(user: dict) -> UserPublic:
    return UserPublic(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        role=user["role"],
        allowed_dashboards=user.get("allowed_dashboards", []),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )
