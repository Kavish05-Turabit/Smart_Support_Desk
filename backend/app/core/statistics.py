import json
from sqlalchemy import select, func, case, cast, Integer
from sqlalchemy.orm import Session
from redis import Redis

from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket
from app.models.validators import TicketResponse,CustomerResponse,EmployeeResponse


async def get_statistics(user, db: Session, redis_client: Redis):

    # tickets , customers , employees , emp_details_data

    dashboard_cache = await redis_client.get("dashboard:admin")
    if dashboard_cache:
        stats = json.loads(dashboard_cache)
        return stats

    try:
        # tickets
        ticket_cache = await redis_client.get("tickets:all")
        if ticket_cache:
            tickets = json.loads(ticket_cache)
        else:
            tickets_data = db.query(Ticket).all()
            tickets = [TicketResponse.model_validate(t).model_dump(mode='json') for t in tickets_data]
            await redis_client.set("tickets:all",json.dumps(tickets),ex=60)

        # customers
        customer_cache = await redis_client.get("customers:all")
        if customer_cache:
            customers = json.loads(customer_cache)
        else:
            customers_data = db.query(Customer).all()
            customers = [CustomerResponse.model_validate(c).model_dump(mode='json') for c in customers_data]
            await redis_client.set("customers:all",json.dumps(customers),ex=60)

        # employees
        employee_cache = await redis_client.get("employees:all")
        if employee_cache:
            employees = json.loads(employee_cache)
        else:
            employees_data = db.query(Employee).all()
            employees = [EmployeeResponse.model_validate(e).model_dump(mode='json') for e in employees_data]
            await redis_client.set("employees:all",json.dumps(employees),ex=60)
    except Exception as e:
        print("Cache Error :- ", e)

    # emp_details_data
    stmt = (
        select(
            Employee.first_name,

            cast(func.sum(case((Ticket.status == 'Open', 1), else_=0)), Integer).label('open_count'),
            cast(func.sum(case((Ticket.status == 'Closed', 1), else_=0)), Integer).label('closed_count'),
            cast(func.sum(case((Ticket.status == 'In Progress', 1), else_=0)), Integer).label('progress_count')
        )
        .join(Ticket, Employee.employee_id == Ticket.assignee_id)
        .group_by(Employee.employee_id, Employee.first_name)
    )
    emp_rows = db.execute(stmt).all()
    emp_details_data = [dict(row._mapping) for row in emp_rows]

    stats = {
        "tickets" : tickets,
        "customers" : customers,
        "employees" : employees,
        "Emp_details" : emp_details_data
    }
    await redis_client.set("dashboard:admin",json.dumps(stats))

    return stats