"""Database session and initialization with migrations."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from alembic.config import Config
from alembic import command

from core.settings import get_settings
from infrastructure.db.base import Base


settings = get_settings()

# Primary database engine (read/write)
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    poolclass=NullPool,
    future=True
)

# Read replica engine (read-only)
read_replica_engine = create_async_engine(
    settings.async_read_replica_database_url,
    echo=settings.debug,
    poolclass=NullPool,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

AsyncReadReplicaSessionLocal = async_sessionmaker(
    read_replica_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields primary database sessions for read/write operations.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_read_replica_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields read replica database sessions for read-only operations.
    Use this for stats, reports, and other read-heavy operations.
    """
    async with AsyncReadReplicaSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def run_migrations() -> None:
    """
    Run Alembic migrations programmatically.
    This applies all pending migrations to the database.
    """
    try:
        print("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise


async def load_fixtures() -> None:
    """
    Load default fixtures into the database.
    """
    try:
        from infrastructure.db.fixtures import load_all_fixtures

        async with AsyncSessionLocal() as session:
            await load_all_fixtures(session)
    except Exception as e:
        print(f"Error loading fixtures: {e}")
        raise


async def init_db() -> None:
    """
    Initialize database by:
    1. Running migrations
    2. Loading default fixtures

    Called on application startup.
    """
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    try:
        from infrastructure.db.models.bidding import (
            associations,
            auction,
            bid,
            bidder,
            supply,
        )
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        raise

    try:
        run_migrations()
        print("✓ Database migrations applied")
    except Exception as e:
        print(f"✗ Migration error: {e}")
        print("Attempting to create tables directly...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tables created directly")

    try:
        await load_fixtures()
        print("✓ Default fixtures loaded")
    except Exception as e:
        print(f"✗ Fixture loading error: {e}")
        raise

    print("=" * 60)
    print("DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)


async def close_db() -> None:
    """
    Close database connection pools.
    Called on application shutdown.
    """
    await engine.dispose()
    await read_replica_engine.dispose()
    print("Database connections closed")
