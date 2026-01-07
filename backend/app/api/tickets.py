from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_tickets():
    return "....List of tickets...."