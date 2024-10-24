"""Logic for creating superuser."""

import asyncio
import contextlib

from pickemApi.models.usermanager import get_user_manager
from pickemApi.database import get_db, get_user_db
from pickemApi.schemas.user import UserSuperIn
from fastapi_users.exceptions import UserAlreadyExists


get_async_session_context = contextlib.asynccontextmanager(get_db)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_superuser(
    email: str, password: str, username: str, is_superuser: bool = True
):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserSuperIn(
                            email=email,
                            password=password,
                            username=username,
                            is_superuser=is_superuser,
                        )
                    )
                    print(f"User created {user}")
                    return user
    except UserAlreadyExists:
        print(f"User {email} already exists")
        raise


if __name__ == "__main__":
    username = input("Enter username for the superuser: ")
    email = input("Enter email for the superuser: ")
    password = input("Enter password for the superuser: ")

    asyncio.run(create_superuser(email, password, username))
