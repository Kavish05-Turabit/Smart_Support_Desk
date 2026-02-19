import json
import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from app.core.session import DBdependency, RedisDependency
from app.models.employeeModel import Employee
from app.models.validators import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.core.security import get_password_hash
from app.core.auth import AdminDependency, AgentDependency

router = APIRouter()
logger = logging.getLogger("EMPLOYEE")


@router.get("/", response_model=List[EmployeeResponse])
async def get_all_employees(db: DBdependency, user: AgentDependency, redis_client: RedisDependency):
    try:
        cache_key = "employees:all"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        employees = db.query(Employee).all()
        data = jsonable_encoder(employees)
        await redis_client.append(cache_key, json.dumps(data))
        return employees
    except Exception as e:
        print("Cache Error :- ", e)
        return db.query(Employee).all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id, db: DBdependency, user: AdminDependency):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID: {employee_id} not found"
        )
    return employee


@router.post("/", response_model=EmployeeResponse)
async def create_employee(employee_in: EmployeeCreate, db: DBdependency, user: AdminDependency,
                          redis_client: RedisDependency):
    try:
        new_employee = Employee(**employee_in.model_dump())
        setattr(new_employee, "password_hash", get_password_hash(getattr(new_employee, "password_hash")))
        db.add(new_employee)
        db.commit()
        await redis_client.delete("employees:all")
        await redis_client.delete("dashboard:admin")

        logger.info(f"User {user.employee_id} created Employee {new_employee.employee_id} with {new_employee.access_level} privilege")
        db.refresh(new_employee)
        return new_employee
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create Employee for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Employee Creation failed."
        )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: int, employee_in: EmployeeUpdate, db: DBdependency, user: AdminDependency,
                          redis_client: RedisDependency):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID: {employee_id} not found"
        )
    data = employee_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(employee, key, value)

    try:
        db.add(employee)
        db.commit()
        await redis_client.delete("employees:all")
        await redis_client.delete("dashboard:admin")

        logger.info(f"User {user.employee_id} updated Employee {employee.employee_id}")
        db.refresh(employee)
        return employee
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update Employee {employee_id} for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Employee cannot be updated right now."
        )


@router.delete("/{employee_id}")
async def delete_employee(employee_id, db: DBdependency, user: AdminDependency, redis_client: RedisDependency):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID: {employee_id} not found"
        )
    try:
        db.delete(employee)
        db.commit()

        logger.info(f"User {user.employee_id} deleted Employee {employee_id}")
        await redis_client.delete("employees:all")
        await redis_client.delete("dashboard:admin")
        return {"message": "Agent deleted succesfully!"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete Employee {employee_id} for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Employee cannot be deleted right now."
        )
