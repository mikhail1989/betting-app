from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import aioredis
from .models import Base
import os

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db():
    """
    Creates all database tables defined in the metadata.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """
    Dependency to get an async database session.

    Yields an async database session.
    """
    async with async_session() as session:
        yield session

async def get_redis():
    """
    Dependency to get an async redis client.

    Yields an async redis client.
    """
    redis = await aioredis.from_url("redis://redis:6379", decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()