from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.core.session import get_db
from app.models.employeeModel import Employee
from app.models.validators import EmployeeCreate,EmployeeResponse,EmployeeUpdate
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/",response_model=List[EmployeeResponse])
def get_all_employees(db: Annotated[Session,Depends(get_db)]):
    employees = db.query(Employee).all()
    return employees

@router.get("/{employee_id}",response_model=EmployeeResponse)
def get_employee(employee_id, db: Annotated[Session, Depends(get_db)]):

    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return "Employee not found"
    return employee

@router.post("/",response_model=EmployeeResponse)
def create_employee(employee_in: EmployeeCreate,db: Annotated[Session,Depends(get_db)]):

    new_employee = Employee(**employee_in.model_dump())
    setattr(new_employee,"password_hash",get_password_hash(getattr(new_employee,"password_hash")))
    db.add(new_employee)
    db.commit()

    db.refresh(new_employee)
    return new_employee

@router.put("/{employee_id}",response_model=EmployeeResponse)
def update_employee(employee_id:int, employee_in: EmployeeUpdate, db: Annotated[Session,Depends(get_db)]):
    
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return "employee not found"
    data = employee_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(employee,key,value)

    db.add(employee)
    db.commit()

    db.refresh(employee)
    return employee