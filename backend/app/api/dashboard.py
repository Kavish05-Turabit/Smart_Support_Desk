from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def show_dashboard():
    return "....Summary Dashboard...."