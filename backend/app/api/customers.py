import json
import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from app.core.session import DBdependency, RedisDependency
from app.core.auth import AgentDependency, AdminDependency
from app.models.customerModel import Customer
from app.models.validators import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter()
logger = logging.getLogger("CUSTOMER")


@router.get("/", response_model=List[CustomerResponse])
async def get_all_customers(db: DBdependency, user: AgentDependency, redis_client: RedisDependency):
    try:
        cache_key = "customers:all"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        customers = db.query(Customer).all()
        data = jsonable_encoder(customers)
        await redis_client.append(cache_key, json.dumps(data))
        return customers
    except Exception as e:
        print("Cache Error :- ", e)
        return db.query(Customer).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id, db: DBdependency, user: AgentDependency):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    return customer


@router.post("/", response_model=CustomerResponse)
async def create_customer(customer_in: CustomerCreate, db: DBdependency, user: AgentDependency,
                          redis_client: RedisDependency):
    try:
        new_customer = Customer(**customer_in.model_dump())
        setattr(new_customer, "created_by", user.employee_id)
        db.add(new_customer)
        db.commit()
        await redis_client.delete("customers:all")
        await redis_client.delete("dashboard:admin")

        logger.info(f"User {user.employee_id} created Customer {new_customer.customer_id}")
        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create Customer for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer Creation failed."
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, customer_in: CustomerUpdate, db: DBdependency, user: AgentDependency,
                          redis_client: RedisDependency):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    data = customer_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(customer, key, value)

    try:
        db.add(customer)
        db.commit()
        await redis_client.delete("customers:all")
        await redis_client.delete("dashboard:admin")

        logger.info(f"User {user.employee_id} updated Customer {customer.customer_id}")
        db.refresh(customer)
        return customer
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update Customer {customer_id} for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer cannot be updated right now."
        )


@router.delete("/{customer_id}")
async def delete_customer(customer_id, db: DBdependency, user: AdminDependency, redis_client: RedisDependency):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    try:
        db.delete(customer)
        db.commit()

        logger.info(f"User {user.employee_id} deleted Customer {customer_id}")
        await redis_client.delete("customers:all")
        await redis_client.delete("dashboard:admin")
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete Customer {customer_id} for User {user.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer cannot be deleted right now."
        )
