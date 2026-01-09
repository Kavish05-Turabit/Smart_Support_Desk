from fastapi import APIRouter
from app.models.employeeModel import Employee
from app.models.customerModel import Customer
from app.models.ticketModel import Ticket

router = APIRouter()

@router.get("/")
def show_dashboard():
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
    return "....Summary Dashboard...."