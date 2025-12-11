import asyncio
from app.db import engine, Base

async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create())