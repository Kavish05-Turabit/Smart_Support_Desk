import json
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from sqlalchemy.orm import joinedload

from app.core.session import DBdependency, RedisDependency
from app.core.auth import AgentDependency, AdminDependency
from app.models.noteModel import Note
from app.models.validators import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter()


@router.get("/{ticket_id}", response_model=List[NoteResponse])
async def get_ticket_notes(ticket_id, db: DBdependency, user: AgentDependency, redis_client: RedisDependency):
    try:
        cache_key = f"notes_for:{ticket_id}"
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        notes = db.query(Note).options(joinedload(Note.author)).filter(Note.ticket_id == ticket_id).all()
        for n in notes:
            n.author_name = f"{n.author.first_name} {n.author.last_name}"

        data = jsonable_encoder(notes)
        await redis_client.set(cache_key, json.dumps(data), ex=60)
        return notes
    except Exception as e:
        print("Cache Error :- ", e)
        return []


@router.post("/{ticket_id}", response_model=NoteResponse)
async def create_note(ticket_id: int, note_in: NoteCreate, db: DBdependency,
                      user: AgentDependency, redis_client: RedisDependency):
    try:
        new_note = Note(**note_in.model_dump())
        setattr(new_note, "ticket_id", ticket_id)
        setattr(new_note, "author_id", user.employee_id)

        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        await redis_client.delete(f"notes_for:{ticket_id}")
        return new_note

    except Exception as e:
        db.rollback()
        print(f"ERROR CREATING NOTE: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Note Creation failed."
        )


@router.put("/{note_id}")
async def edit_note(note_id: int, note_in: NoteCreate, db: DBdependency,
                    user: AgentDependency, redis_client: RedisDependency):
    note = db.query(Note).filter(Note.note_id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"note with ID: {note_id} not found."
        )

    data = note_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(note, key, value)

    try:
        db.add(note)
        db.commit()

        await redis_client.delete(f"notes_for:{note.ticket_id}")

        db.refresh(note)
        return {"message": "Note Updated Successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Note cannot be updated right now."
        )
