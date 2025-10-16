from typing import AsyncGenerator
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.database import AsyncSessionLocal

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session