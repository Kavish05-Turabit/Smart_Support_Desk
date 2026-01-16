from fastapi import APIRouter
import json
from sqlalchemy import select, func, case

from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket
from app.core.session import RedisDependency, DBdependency
from app.core.auth import AgentDependency
from app.core.statistics import get_statistics

router = APIRouter()


@router.get("/")
async def show_dashboard(db: DBdependency, redis_client: RedisDependency, user: AgentDependency):
    
    statistics = get_statistics(user, db, redis_client)
    return await statistics
