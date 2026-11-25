"""
Database Schema Initializer.
Ensures target database exists and creates all registered tables defined in SQLAlchemy models.

Usage:
    python -m app.database.init_db
"""

import sys
from sqlalchemy import text
from app.database.session import engine, ensure_database_exists
from app.database.base import Base
from app.database.models import (
    Destination,
    Topic,
    Article,
    ResearchSource,
    ImageAsset,
    PublishingJob,
)
from app.utils.logging import logger


def init_db() -> bool:
    """
    Initializes database schema by:
    1. Ensuring the target PostgreSQL database exists (auto-created if missing)
    2. Checking for pgvector extension (for Level 2 semantic duplicate search)
    3. Creating all registered tables if they do not exist
    """
    logger.info("Initializing GlobeTrotter AI database schema...")
    try:
        # Step 1: Ensure target database exists
        ensure_database_exists()

        # Step 2: Check optional pgvector extension
        if "postgresql" in engine.dialect.name:
            try:
                with engine.connect() as conn:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                    logger.info("[+] pgvector extension checked/enabled.")
            except Exception:
                # Informational: pgvector is optional on Windows; Level 1 canonical deduplication is primary
                logger.info(
                    "[i] Optional pgvector extension is not installed in local PostgreSQL. "
                    "Level-1 Canonical deduplication is fully active."
                )

        # Step 3: Create all registered SQLAlchemy tables
        Base.metadata.create_all(bind=engine)
        logger.info("[+] Database tables successfully created / verified:")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"    - {table_name}")
        return True
    except Exception as exc:
        logger.error(f"[-] Failed to initialize database: {exc}")
        return False


if __name__ == "__main__":
    success = init_db()
    if not success:
        sys.exit(1)
