"""
Database Session, Connection Engine, and Automated Database Provisioning.
Supports automatic PostgreSQL database creation if it does not already exist.
"""

from typing import Generator, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()


def ensure_database_exists(db_url: Optional[str] = None) -> bool:
    """
    Checks if the target database exists in PostgreSQL.
    If the database does not exist, connects to the administrative 'postgres' database
    and creates the target database automatically with UTF-8 encoding.
    """
    target_url_str = db_url or settings.DATABASE_URL
    url = make_url(target_url_str)

    # SQLite creates the file automatically, so no separate database creation is needed
    if "postgresql" not in url.drivername:
        return True

    target_dbname = url.database
    if not target_dbname or target_dbname in ("postgres", "template1"):
        return True

    try:
        # Connect to maintenance database 'postgres' with autocommit enabled
        admin_url = url.set(database="postgres")
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

        with admin_engine.connect() as conn:
            check_query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            exists = conn.execute(check_query, {"dbname": target_dbname}).scalar()

            if not exists:
                logger.info(f"Target database '{target_dbname}' not found. Creating automatically...")
                # Note: database names in DDL cannot use bind parameters directly
                conn.execute(text(f'CREATE DATABASE "{target_dbname}" ENCODING \'UTF8\';'))
                logger.info(f"[+] Successfully created PostgreSQL database '{target_dbname}'.")
            else:
                logger.debug(f"[+] PostgreSQL database '{target_dbname}' already exists.")

        admin_engine.dispose()
        return True
    except Exception as exc:
        logger.error(f"[-] Automated database verification/creation error for '{target_dbname}': {exc}")
        return False


# Attempt automatic database creation on startup
ensure_database_exists()

# Engine creation with connection pooling for PostgreSQL
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DB_ECHO,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=10,     # Prevent connection pool starvation lockups
        pool_recycle=1800,   # Recycle connections every 30 minutes to prevent stale TCP sockets
        pool_pre_ping=True,  # Automatically detects and discards stale/dead connections
        echo=settings.DB_ECHO,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Ensures sessions are cleanly closed when requests finish.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """
    Checks live database connectivity and returns database engine metadata.
    Ensures target database exists before attempting connection.
    """
    try:
        # Ensure database is present
        ensure_database_exists()

        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            result.scalar()

            # Mask credentials from URL for secure reporting
            safe_url = str(engine.url)
            if "@" in safe_url:
                prefix = safe_url.split("@")[0]
                host_part = safe_url.split("@")[1]
                safe_url = f"{prefix.split(':')[0]}://***:***@{host_part}"

            return {
                "status": "connected",
                "database": engine.url.database,
                "dialect": engine.dialect.name,
                "url": safe_url,
            }
    except Exception as exc:
        logger.error(f"Database connection error: {exc}")
        return {
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "configured_database": engine.url.database,
        }
