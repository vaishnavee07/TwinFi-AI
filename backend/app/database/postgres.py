from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

try:
    import aiosqlite  # noqa: F401
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False

if HAS_AIOSQLITE:
    logger.info("✅ aiosqlite driver detected. Initializing async database engine.")
    # Async Engine (supports SQLite and PostgreSQL)
    engine_args = {
        "echo": (settings.ENVIRONMENT == "development")
    }

    if settings.DATABASE_URL.startswith("sqlite"):
        engine_args["connect_args"] = {"timeout": 30}
    else:
        engine_args["pool_size"] = 10
        engine_args["max_overflow"] = 5
        engine_args["pool_pre_ping"] = True
        engine_args["pool_recycle"] = 3600

    engine = create_async_engine(
        settings.DATABASE_URL,
        **engine_args
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async def get_db():
        """FastAPI dependency — yields an async DB session."""
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def init_db():
        """Create all tables on startup."""
        async with engine.begin() as conn:
            from app.models import user, customer_profile, bank_account, transaction  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
            logger.info("SQLite/SQLAlchemy database tables initialized.")

else:
    logger.warning("⚠️  aiosqlite driver not installed. Falling back to native synchronous SQLite wrapper.")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    engine = create_engine(sync_url, connect_args={"timeout": 30})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    class SyncToAsyncSessionWrapper:
        """Adapts synchronous SQLAlchemy Session to behave like AsyncSession."""
        def __init__(self, sync_session):
            self.sync_session = sync_session

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.sync_session.close()

        async def execute(self, statement, *args, **kwargs):
            return self.sync_session.execute(statement, *args, **kwargs)

        async def commit(self):
            self.sync_session.commit()

        async def rollback(self):
            self.sync_session.rollback()

        async def close(self):
            self.sync_session.close()

        def add(self, instance):
            self.sync_session.add(instance)

        async def delete(self, instance):
            self.sync_session.delete(instance)

        async def flush(self):
            self.sync_session.flush()

    def AsyncSessionLocal():
        return SyncToAsyncSessionWrapper(SessionLocal())

    async def get_db():
        """FastAPI dependency using synchronous SQLite session wrapper."""
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def init_db():
        """Create all tables synchronously on startup."""
        from app.models import user, customer_profile, bank_account, transaction  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("SQLite database tables initialized (synchronous fallback).")
