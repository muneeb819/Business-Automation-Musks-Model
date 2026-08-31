from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import make_url
from app.core.config import settings
import ssl


def _create_engine():
    url = make_url(settings.DATABASE_URL)
    # asyncpg doesn't support query params like sslmode in the URL.
    # Extract SSL params and pass via connect_args.
    query = dict(url.query)
    connect_args = {}

    if query.get("sslmode") in ("require", "verify-ca", "verify-full"):
        ssl_ctx = ssl.create_default_context()
        if query.get("sslmode") == "require":
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    # asyncpg doesn't use channel_binding param directly
    # (handled by ssl context)

    # Remove query params so URL is clean for asyncpg
    url = url.set(query={})

    return create_async_engine(
        url,
        echo=settings.DATABASE_ECHO,
        pool_size=20,
        max_overflow=10,
        connect_args=connect_args,
    )


engine = _create_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
