from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
import json

from app.core.session import DBdependency,RedisDependency
from app.models.employeeModel import Employee
from app.models.validators import EmployeeCreate,EmployeeResponse,EmployeeUpdate
from app.core.security import get_password_hash
from app.core.auth import AdminDependency,ViewerDependency

router = APIRouter()

@router.get("/",response_model=List[EmployeeResponse])
async def get_all_employees(db: DBdependency,user: ViewerDependency,redis_client: RedisDependency):
    cache_key = "employees:all"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    employees = db.query(Employee).all()
    data = jsonable_encoder(employees)
    await redis_client.append(cache_key,json.dumps(data))
    return employees

@router.get("/{employee_id}",response_model=EmployeeResponse)
def get_employee(employee_id, db: DBdependency,user: ViewerDependency):

    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return "Employee not found"
    return employee

@router.post("/",response_model=EmployeeResponse)
async def create_employee(employee_in: EmployeeCreate,db: DBdependency,user: AdminDependency,redis_client: RedisDependency):

    new_employee = Employee(**employee_in.model_dump())
    setattr(new_employee,"password_hash",get_password_hash(getattr(new_employee,"password_hash")))
    db.add(new_employee)
    db.commit()
    await redis_client.delete("employees:all")

    db.refresh(new_employee)
    return new_employee

@router.put("/{employee_id}",response_model=EmployeeResponse)
async def update_employee(employee_id:int, employee_in: EmployeeUpdate, db: DBdependency,user: AdminDependency,redis_client: RedisDependency):
    
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return "employee not found"
    data = employee_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(employee,key,value)

    db.add(employee)
    db.commit()
    await redis_client.delete("employees:all")

    db.refresh(employee)
    return employee

@router.delete("/{employee_id}",response_model=EmployeeResponse)
async def delete_employee(employee_id, db: DBdependency,user: AdminDependency,redis_client: RedisDependency):

    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return "Employee not found"
    db.delete(employee)
    db.commit()
    await redis_client.delete("employees:all")
    return employee