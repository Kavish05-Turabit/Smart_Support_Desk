from fastapi import APIRouter
import json

from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket
from app.core.session import RedisDependency,DBdependency
from app.core.auth import EditorDependency

router = APIRouter()

@router.get("/")
async def show_dashboard(db: DBdependency,redis_client: RedisDependency,user: EditorDependency):
    cached_data = await redis_client.get("dashboard:all")
    if cached_data:
        return json.loads(cached_data)
    Customer_count = db.query(Customer).count()
    Employee_count = db.query(Employee).count()
    Ticket_count = db.query(Ticket).count()
    
    statistics = {
        "Customer_count" : Customer_count,
        "Employee_count" : Employee_count,
        "Ticket_count" : Ticket_count,
    }

    return statistics