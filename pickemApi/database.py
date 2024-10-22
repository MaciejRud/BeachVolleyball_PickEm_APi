"""
Set up database.
"""

from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from fastapi_users.db import SQLAlchemyUserDatabase

from pickemApi.models.model import User, Base

from contextlib import asynccontextmanager
from config import config


engine = create_async_engine(
    config.DATABASE_URL, connect_args={"check_same_thread": False}
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


# Dependency do uzyskiwania sesji
async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
            if config.DB_FORCE_ROLL_BACK:  # Sprawdź flagę z configu
                await db.rollback()  # Asynchronicznie wycofaj zmiany podczas testów
            else:
                await db.commit()  # Domyślna transakcja
        except Exception:
            await db.rollback()  # Zawsze wycofaj w przypadku wyjątku
            raise


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)
