from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from app.core.config import settings
from app.core.security import hash_password
from app.schemas import default_dashboards_for_role


def build_user(username: str, email: str, password: str, role: str, full_name: str):
    return {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hash_password(password),
        "role": role,
        "allowed_dashboards": default_dashboards_for_role(role),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }


def main():
    client = MongoClient(settings.mongo_uri)
    db = client[settings.db_name]

    users = [
        build_user("admin01", "admin01@example.com", "12345678", "admin", "System Admin"),
        build_user("operator01", "operator01@example.com", "12345678", "operator", "Vision Operator"),
        build_user("viewer01", "viewer01@example.com", "12345678", "viewer", "Dashboard Viewer"),
    ]

    try:
        result = db.users.insert_many(users, ordered=False)
        print("Inserted user ids:", result.inserted_ids)
    except BulkWriteError as exc:
        print("Some users may already exist.")
        print(exc.details)

    client.close()


if __name__ == "__main__":
    main()
