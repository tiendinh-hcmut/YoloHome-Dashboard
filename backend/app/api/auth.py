from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from ..core.database import get_db
from ..core.security import create_access_token, get_current_user, hash_password, verify_password, require_roles
from ..schemas import UserCreate, UserPublic, TokenResponse, default_dashboards_for_role, user_to_public

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db=Depends(get_db)):
    user_doc = {
        "username": payload.username,
        "email": payload.email,
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "allowed_dashboards": default_dashboards_for_role(payload.role),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    created = await db.users.find_one({"_id": result.inserted_id})
    return user_to_public(created)


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db),
):
    user = await db.users.find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {
            "sub": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_to_public(user),
    )


@router.get("/me", response_model=UserPublic)
async def read_me(current_user=Depends(get_current_user)):
    return user_to_public(current_user)


@router.get("/users", response_model=list[UserPublic])
async def list_users(
    current_user=Depends(require_roles("admin")),
    db=Depends(get_db),
):
    items = []
    async for user in db.users.find().sort("created_at", -1):
        items.append(user_to_public(user))
    return items
