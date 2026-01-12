import json
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from app.core.session import DBdependency,RedisDependency
from app.core.auth import EditorDependency,AdminDependency
from app.models.ticketModel import Ticket
from app.models.validators import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter()

@router.get("/",response_model=List[TicketResponse])
async def get_all_tickets(db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    try:
        cache_key = "tickets:all"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        tickets = db.query(Ticket).all()
        data = jsonable_encoder(tickets)
        await redis_client.set(cache_key,json.dumps(data),ex=60)
        return tickets
    except Exception as e:
        print("Cache Error :- ",e)
        return db.query(Ticket).all()

@router.get("/{ticket_id}",response_model=TicketResponse)
def get_ticket(ticket_id, db: DBdependency,user: EditorDependency):

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID: {ticket_id} not found"
        )
    return ticket

@router.post("/",response_model=TicketResponse)
async def create_ticket(ticket_in: TicketCreate,db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    try:
        new_ticket = Ticket(**ticket_in.model_dump())
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        await redis_client.delete("tickets:all")
        return new_ticket
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket Creation failed."
        )

@router.put("/{ticket_id}",response_model=TicketResponse)
async def update_ticket(ticket_id:int, ticket_in: TicketUpdate, db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID: {ticket_id} not found."
        )
    data = ticket_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(ticket,key,value)
        
    try:
        db.add(ticket)
        db.commit()
        await redis_client.delete("tickets:all")

        db.refresh(ticket)
        return ticket
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket cannot be updated right now."
        )

@router.delete("/{ticket_id}",response_model=TicketResponse)
async def delete_ticket(ticket_id, db: DBdependency,user: AdminDependency,redis_client: RedisDependency):

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID: {ticket_id} not found."
        )
    try:
        db.delete(ticket)
        db.commit()
        await redis_client.delete("tickets:all")
        return {"message" : "Ticket deleted succesfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket cannot be deleted right now."
        )