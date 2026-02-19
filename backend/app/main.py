from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import tickets, dashboard, customers, employees, login, notes, chat
from app.core.config import settings
from app.core.session import engine, Base
import app.core.session as sess
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError as RedisConnectionError

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = sess.redisDb = aioredis.from_url(
        "redis://localhost:32768",
        decode_responses=True
    )
    try:
        await r.ping()
        sess.redisDb = r
    except RedisConnectionError:
        sess.redisDb = sess.MockRedis()
        await r.close()

    yield
    print("Closing the Database connection")
    engine.dispose()
    print("Closed the Database connection")

    print("Closing the Redis connection")
    await sess.redisDb.close()
    print("Closed the Redis connection")


app = FastAPI(title="Smart Support Desk", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,  # Allows cookies/auth headers
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(login.router, prefix="/login", tags=["Login"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(employees.router, prefix="/employees", tags=["Employees"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
def root():
    return f"Welcome to Smart support system , this is {settings.BASE}"
