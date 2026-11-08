import aiosqlite
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Context manager for SQLite connection with Row factory."""
    db = await aiosqlite.connect(settings.DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    """Initializes the database schema if not already present."""
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                url TEXT,
                company_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                geographic_scope TEXT NOT NULL,
                content_analysis TEXT NOT NULL,
                competitors TEXT NOT NULL,
                comparison_table TEXT NOT NULL,
                swot TEXT NOT NULL,
                gap_analysis TEXT NOT NULL,
                strategic_recommendations TEXT NOT NULL,
                executive_summary TEXT NOT NULL,
                overall_score REAL NOT NULL DEFAULT 8.0,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()
        logger.info("Database initialized successfully at: %s", settings.DATABASE_PATH)
