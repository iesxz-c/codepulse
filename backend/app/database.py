from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings
import logging

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    import os
    from sqlalchemy import text
    
    init_sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations", "init.sql")
    if os.path.exists(init_sql_path):
        with open(init_sql_path, "r") as f:
            sql = f.read()
            try:
                # With asyncpg, multiple statements must be run via the raw connection
                async with engine.begin() as conn:
                    raw_conn = await conn.get_raw_connection()
                    await raw_conn.driver_connection.execute(sql)
                logging.info("Database initialized successfully.")
            except Exception as e:
                logging.error(f"Error initializing database: {e}")
