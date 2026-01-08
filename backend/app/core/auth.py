import jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.session import get_db
from typing import Annotated
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.core.config import settings
from app.models.employeeModel import Employee

db_dependency = Annotated[Session,Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(db: db_dependency,email: str,password: str):
    user = db.query(Employee).filter(Employee.email == email).first()
    if not user:
        return False
    if not verify_password(password,user.password_hash):
        return False
    return user

def create_access_token(data: dict,expires: timedelta | None = None):
    to_encode = data.copy()
    if expires:
        expire = datetime.now() + expires
    else:
        expire = datetime.now() + timedelta(minutes=30)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,settings.JWT_SHA256_HASH,settings.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(db: db_dependency,token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SHA256_HASH, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = db.query(Employee).filter(Employee.email == email).first()
    if user is None:
        raise credentials_exception
    return user