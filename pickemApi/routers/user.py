# app/routers/user.py

from fastapi import APIRouter, Depends
from pickemApi.models.model import User
from pickemApi.core.security import auth_backend
from pickemApi.models.usermanager import fastapi_users, current_active_user
from pickemApi.schemas.user import UserIn, UserResponse

router = APIRouter()

# Dodaj endpointy do routera
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserResponse, UserIn),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserResponse),
    prefix="/auth",
    tags=["auth"],
)


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
