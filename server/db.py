import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
from contextlib import asynccontextmanager, contextmanager

# Cargar variables de entorno
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_HOST_PORT", "5432")

# URLs para ambos engines
ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
SYNC_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Engine y sessionmaker asíncronos
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Engine y sessionmaker síncronos
sync_engine = create_engine(SYNC_DATABASE_URL, echo=False, future=True)
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)

# Base para los modelos
Base = declarative_base()

# Context manager asíncrono
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def session_context():
    async with AsyncSessionLocal() as session:
        yield session

# Context manager síncrono
@contextmanager
def session_context_sync() -> Generator:
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
