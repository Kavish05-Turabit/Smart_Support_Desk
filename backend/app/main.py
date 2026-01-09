from fastapi import FastAPI
from app.api import tickets,dashboard,customers,employees,login
from app.core.config import settings
from app.core.session import engine,Base
import app.core.session as sess
from contextlib import asynccontextmanager
from redis import asyncio as aioredis

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    sess.redisDb = aioredis.from_url(
        "redis://localhost:32769",
        decode_responses = True
    )
    yield
    print("Closing the Database connection")
    engine.dispose()
    print("Closing the Redis connection")
    await sess.redisDb.close()

app = FastAPI(title="Smart Support Desk",lifespan=lifespan)

app.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
app.include_router(login.router,prefix="/login",tags=["Login"])
app.include_router(tickets.router,prefix="/tickets",tags=["Tickets"])
app.include_router(customers.router,prefix="/customers",tags=["Customers"])
app.include_router(employees.router,prefix="/employees",tags=["Employees"])

@app.get("/")
def root():
    return f"Welcome to Smart support system , this is {settings.BASE}"  