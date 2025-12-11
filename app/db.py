from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends


# ——— DATABASE CONFIG (MySQL async) ———
DATABASE_URL = "mysql+aiomysql://mhd:mehdi123@mysql-mhd.alwaysdata.net/mhd_user1"

class Base(DeclarativeBase):
    pass


# ——— PLAYER MODEL (matches SQL file) ———
class Player(Base):
    __tablename__ = "players"

    id = Column("COL 1", String(9), primary_key=True)
    name = Column("COL 4", String(32))
    last_season = Column("COL 5", String(11))
    citizenship = Column("COL 10", String(24))
    image_url = Column("COL 18", String(91))
    current_club_name = Column("COL 21", String(98))
    stat_value = Column("COL 22", Integer)


# ——— ENGINE & SESSION ———
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
