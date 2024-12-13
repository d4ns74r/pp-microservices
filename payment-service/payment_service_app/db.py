from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/payment_service"

engine = create_async_engine(DATABASE_URL, echo=True)

# Асинхронный sessionmaker
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


# Dependency для работы с БД
async def get_db():
    async with async_session() as session:
        yield session
