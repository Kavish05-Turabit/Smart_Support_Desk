from fastapi import FastAPI
from app.api import tickets,dashboard,customers,employees
from app.core.config import settings
from app.core.session import engine,Base
from contextlib import asynccontextmanager

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan():
    
    yield
    print("Closing the Database connection")
    engine.dispose()

app = FastAPI(title="Smart Support Desk")

app.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
app.include_router(tickets.router,prefix="/tickets",tags=["Tickets"])
app.include_router(customers.router,prefix="/customers",tags=["Customers"])
app.include_router(employees.router,prefix="/employees",tags=["Employees"])

@app.get("/")
def root():
    return f"Welcome to Smart support system , this is {settings.BASE}"  