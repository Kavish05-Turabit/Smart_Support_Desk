import json
from fastapi import APIRouter, HTTPException,status
from fastapi.encoders import jsonable_encoder
from typing import List

from app.core.session import DBdependency,RedisDependency
from app.core.auth import EditorDependency,AdminDependency
from app.models.customerModel import Customer
from app.models.validators import CustomerCreate,CustomerResponse,CustomerUpdate

router = APIRouter()

@router.get("/",response_model=List[CustomerResponse])
async def get_all_customers(db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    try:    
        cache_key = "customers:all"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        customers = db.query(Customer).all()
        data = jsonable_encoder(customers)
        await redis_client.append(cache_key,json.dumps(data))
        return customers
    except Exception as e:
        print("Cache Error :- ",e)
        return db.query(Customer).all()

@router.get("/{customer_id}",response_model=CustomerResponse)
def get_customer(customer_id, db: DBdependency,user: EditorDependency):

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    return customer

@router.post("/",response_model=CustomerResponse)
async def create_customer(customer_in: CustomerCreate,db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    try:
        new_customer = Customer(**customer_in.model_dump())
        setattr(new_customer,"created_by",user.employee_id)
        db.add(new_customer)
        db.commit()
        await redis_client.delete("customers:all")

        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer Creation failed."
        )

@router.put("/{customer_id}",response_model=CustomerResponse)
async def update_customer(customer_id:int, customer_in: CustomerUpdate, db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    data = customer_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(customer,key,value)

    try:
        db.add(customer)
        db.commit()
        await redis_client.delete("customers:all")

        db.refresh(customer)
        return customer
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer cannot be updated right now."
        )

@router.delete("/{customer_id}",response_model=CustomerResponse)
async def delete_customer(customer_id, db: DBdependency,user: AdminDependency,redis_client: RedisDependency):

    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID: {customer_id} not found"
        )
    try:
        db.delete(customer)
        db.commit()
        await redis_client.delete("customers:all")
        return {"message" : "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Customer cannot be deleted right now."
        )