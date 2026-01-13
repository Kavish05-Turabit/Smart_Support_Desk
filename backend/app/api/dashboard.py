from fastapi import APIRouter
import json
from sqlalchemy import select, func, case

from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket
from app.core.session import RedisDependency, DBdependency
from app.core.auth import AgentDependency

router = APIRouter()


@router.get("/")
async def show_dashboard(db: DBdependency, redis_client: RedisDependency, user: AgentDependency):
    cached_data = await redis_client.get("dashboard:all")
    if cached_data:
        return json.loads(cached_data)
    
    tickets = db.query(Ticket).all()
    tickets_data = [
        {c.name: getattr(ticket, c.name) for c in ticket.__table__.columns}
        for ticket in tickets
    ]

    Customer_count = db.query(Customer).count()
    Employee_count = db.query(Employee).count()
    Ticket_count = db.query(Ticket).count()

    stmt = (
        select(
            Employee.first_name,
            # Count tickets where status is 'Open'
            func.sum(case((Ticket.status == 'Open', 1), else_=0)).label('open_count'),
            
            # Count tickets where status is 'Closed'
            func.sum(case((Ticket.status == 'Closed', 1), else_=0)).label('closed_count'),
            
            # Count tickets where status is 'In Progress'
            func.sum(case((Ticket.status == 'In Progress', 1), else_=0)).label('progress_count')
        )
        .join(Ticket, Employee.employee_id == Ticket.assignee_id)
        .group_by(Employee.employee_id, Employee.first_name)
    )

    # Execute the query
    emp_rows = db.execute(stmt).all()
    emp_details_data = [dict(row._mapping) for row in emp_rows]

    statistics = {
        "tickets" : tickets_data,
        "Customer_count": Customer_count,
        "Employee_count": Employee_count,
        "Ticket_count": Ticket_count,
        "Emp_details" : emp_details_data
    }

    return statistics
