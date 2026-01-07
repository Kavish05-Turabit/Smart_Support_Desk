from fastapi import FastAPI
from app.api import tickets,dashboard
from .core.config import settings

app = FastAPI(title="Smart Support Desk")

app.include_router(tickets.router,prefix="/tickets",tags=["Tickets"])
app.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])

@app.get("/")
def root():
    return f"Welcome to Smart support system , this is {settings.BASE}"