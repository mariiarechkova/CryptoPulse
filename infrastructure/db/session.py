from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

# 1. Creating an engine
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Session Factory
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

# 3. The base class of models
class Base(DeclarativeBase):
    pass

# 4. generator for getting a session
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session