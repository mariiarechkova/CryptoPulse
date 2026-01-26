from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def try_advisory_lock(session: AsyncSession, key: int) -> bool:
    # returns true if lock acquired
    res = await session.execute(text("SELECT pg_try_advisory_lock(:key)"), {"key": key})
    return bool(res.scalar())


async def advisory_unlock(session: AsyncSession, key: int) -> None:
    await session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
