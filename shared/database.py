from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    pass


engine: Optional[AsyncEngine] = None
session_maker: Optional[async_sessionmaker[AsyncSession]] = None


async def init_db() -> None:
    global engine, session_maker
    engine = create_async_engine(
        settings.database_url, echo=False
    )  # Set echo=True for SQL logging in dev
    session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def close_db() -> None:
    global engine
    if engine:
        await engine.dispose()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    if not session_maker:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
