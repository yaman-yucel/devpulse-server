import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://afaruk:158158158@localhost:5452/last_tracker_db"
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# ✅ Now async, so it can be awaited in the lifespan
async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
