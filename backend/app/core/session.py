from redis.asyncio import Redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from fastapi import Depends
from typing import Annotated

engine = create_engine(
    url=settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10
)

Sessionlocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


DBdependency = Annotated[Session, Depends(get_db)]

redisDb = None


def get_redis():
    if not redisDb:
        return False
    return redisDb


RedisDependency = Annotated[Redis, Depends(get_redis)]
