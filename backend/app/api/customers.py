from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.core.session import get_db
from app.core.auth import get_current_user
from app.models.customerModel import Customer
from app.models.employeeModel import Employee
from app.models.validators import CustomerCreate,CustomerResponse,CustomerUpdate

router = APIRouter()

@router.get("/",response_model=List[CustomerResponse])
def get_all_customers(db: Annotated[Session,Depends(get_db)]):
    customers = db.query(Customer).all()
    return customers

@router.get("/{customer_id}",response_model=CustomerResponse)
def get_customer(customer_id, db: Annotated[Session, Depends(get_db)]):

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return "Customer not found"
    return customer

@router.post("/",response_model=CustomerResponse)
def create_customer(customer_in: CustomerCreate,db: Annotated[Session,Depends(get_db)],user: Employee = Depends(get_current_user)):

    new_customer = Customer(**customer_in.model_dump())
    setattr(new_customer,"created_by",user.employee_id)
    db.add(new_customer)
    db.commit()

    db.refresh(new_customer)
    return new_customer

@router.put("/{customer_id}",response_model=CustomerResponse)
def update_customer(customer_id:int, customer_in: CustomerUpdate, db: Annotated[Session,Depends(get_db)]):
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return "Customer not found"
    data = customer_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(customer,key,value)

    db.add(customer)
    db.commit()

    db.refresh(customer)
    return customer