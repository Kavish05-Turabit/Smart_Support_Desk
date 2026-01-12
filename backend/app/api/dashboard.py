from fastapi import APIRouter
import json

from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket
from app.core.session import RedisDependency,DBdependency
from app.core.auth import ViewerDependency

router = APIRouter()

@router.get("/")
async def show_dashboard(db: DBdependency,redis_client: RedisDependency,user: ViewerDependency):
    statistics = {
        "Customer_count" : 0,
        "Employee_count" : 0,
        "Ticket_count" : 0,
        "Tickets" : 0,
        "Total_open_tickets" : 0,
        "Total_assigned_tickets" : 0,
        "Total_closed_tickets" : 0,
        "Ticket_current_week" : 0
    }
    statistics["Customer_count"] = db.query(Customer).count()
    statistics["Employee_count"] = db.query(Employee).count()
    statistics["Ticket_count"] = db.query(Ticket).count()
    tickets = await redis_client.get("tickets:all")
    if not tickets:
        statistics["Tickets"] = db.query(Ticket).all()
    else:
        statistics["Tickets"] = json.loads(tickets)
    for ticket in tickets:
        if ticket["status"] == "Open":
            statistics["Total_open_tickets"] += 1
        if ticket["status"] == "Open":
            statistics["Total_open_tickets"] += 1
        if ticket["status"] == "Open":
            statistics["Total_open_tickets"] += 1
        
    return statistics