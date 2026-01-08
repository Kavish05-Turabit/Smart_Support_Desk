from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.core.session import get_db
from app.models.ticketModel import Ticket
from app.models.validators import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter()

@router.get("/",response_model=List[TicketResponse])
def get_all_tickets(db: Annotated[Session,Depends(get_db)]):
    
    tickets = db.query(Ticket).all()
    return tickets

@router.get("/{ticket_id}",response_model=TicketResponse)
def get_ticket(ticket_id, db: Annotated[Session, Depends(get_db)]):

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return "Ticket not found"
    return ticket

@router.post("/",response_model=TicketResponse)
def create_ticket(ticket_in: TicketCreate,db: Annotated[Session,Depends(get_db)]):

    new_ticket = Ticket(**ticket_in.model_dump())
    db.add(new_ticket)
    db.commit()

    db.refresh(new_ticket)
    return new_ticket

@router.put("/{ticket_id}",response_model=TicketResponse)
def update_ticket(ticket_id:int, ticket_in: TicketUpdate, db: Annotated[Session,Depends(get_db)]):
    
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        return "Ticket not found"
    data = ticket_in.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(ticket,key,value)

    db.add(ticket)
    db.commit()

    db.refresh(ticket)
    return ticket