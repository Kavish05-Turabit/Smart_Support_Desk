import json
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional

from app.core.session import DBdependency, RedisDependency
from app.core.auth import AgentDependency, AdminDependency
from app.models.ticketModel import Ticket
from app.models.validators import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter()


@router.get("/", response_model=List[TicketResponse])
async def get_all_tickets(db: DBdependency, user: AgentDependency, redis_client: RedisDependency,
                          skip: int = 0,limit: Optional[int] = None):
    try:
        cache_key = "tickets:all"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        if not limit:
            tickets = db.query(Ticket).all()
            data = jsonable_encoder(tickets)
            await redis_client.set(cache_key, json.dumps(data), ex=60)
        else:
            tickets = db.query(Ticket).offset(skip).limit(limit).all()
        return tickets
    except Exception as e:
        print("Cache Error :- ", e)
        if not limit:
            return db.query(Ticket).all()
        return db.query(Ticket).offset(skip).limit(limit).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id, db: DBdependency, user: AgentDependency):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID: {ticket_id} not found"
        )
    return ticket


@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket_in: TicketCreate, db: DBdependency, user: AgentDependency,
                        redis_client: RedisDependency):
    try:
        new_ticket = Ticket(**ticket_in.model_dump())
        setattr(new_ticket, "created_by_id", user.employee_id)
        if getattr(new_ticket,"assignee_id") == 0:
            setattr(new_ticket, "assignee_id", None)
        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        await redis_client.delete("tickets:all")
        await redis_client.delete("dashboard:admin")
        return new_ticket

    except Exception as e:
        db.rollback()
        print(f"ERROR CREATING TICKET: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket Creation failed."
        )


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: int, ticket_in: TicketUpdate, db: DBdependency, user: AgentDependency,
                        redis_client: RedisDependency):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID: {ticket_id} not found."
        )
    data = ticket_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(ticket, key, value)

    try:
        db.add(ticket)
        db.commit()
        await redis_client.delete("tickets:all")
        await redis_client.delete("dashboard:admin")

        db.refresh(ticket)
        return ticket
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket cannot be updated right now."
        )


@router.delete("/{ticket_id}")
async def delete_ticket(ticket_id, db: DBdependency, user: AdminDependency, redis_client: RedisDependency):
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
        await redis_client.delete("dashboard:admin")
        return {"message": "Ticket deleted succesfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Ticket cannot be deleted right now."
        )
