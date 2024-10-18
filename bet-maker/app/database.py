from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .models import Base
import os

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
