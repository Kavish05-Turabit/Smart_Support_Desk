from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List
from redis.asyncio import Redis
from fastapi.encoders import jsonable_encoder
import json

from app.core.session import DBdependency,RedisDependency
from app.core.auth import EditorDependency,ViewerDependency
from app.models.ticketModel import Ticket
from app.models.validators import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter()

@router.get("/",response_model=List[TicketResponse])
async def get_all_tickets(db: DBdependency,user: ViewerDependency,redis_client: RedisDependency):
    cache_key = "tickets:all"
    cached_data = await redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    tickets = db.query(Ticket).all()
    data = jsonable_encoder(tickets)
    await redis_client.append(cache_key,json.dumps(data))
    return tickets

@router.get("/{ticket_id}",response_model=TicketResponse)
def get_ticket(ticket_id, db: DBdependency,user: ViewerDependency):

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return "Ticket not found"
    return ticket

@router.post("/",response_model=TicketResponse)
async def create_ticket(ticket_in: TicketCreate,db: DBdependency,user: EditorDependency,redis_client: RedisDependency):

    new_ticket = Ticket(**ticket_in.model_dump())
    db.add(new_ticket)
    db.commit()
    await redis_client.delete("tickets:all")

    db.refresh(new_ticket)
    return new_ticket

@router.put("/{ticket_id}",response_model=TicketResponse)
async def update_ticket(ticket_id:int, ticket_in: TicketUpdate, db: DBdependency,user: EditorDependency,redis_client: RedisDependency):
    
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return "Ticket not found"
    data = ticket_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(ticket,key,value)

    db.add(ticket)
    db.commit()
    await redis_client.delete("tickets:all")

    db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}",response_model=TicketResponse)
async def delete_ticket(ticket_id, db: DBdependency,user: ViewerDependency,redis_client: RedisDependency):

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return "Ticket not found"
    db.delete(ticket)
    db.commit()
    await redis_client.delete("tickets:all")
    return ticket