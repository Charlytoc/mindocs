import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
from contextlib import asynccontextmanager, contextmanager

# Cargar variables de entorno
load_dotenv()


# URLs para ambos engines
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("DATABASE_URL")

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
