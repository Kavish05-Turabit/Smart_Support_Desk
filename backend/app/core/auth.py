import jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.session import DBdependency
from typing import Annotated
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.core.config import settings
from app.models.employeeModel import Employee

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def authenticate_user(db: DBdependency,email: str,password: str):
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

async def get_current_user(db: DBdependency,token: Annotated[str, Depends(oauth2_scheme)]):
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

class RoleDependency:
    def __init__(self,required_level):
        self.required_level = required_level

    def __call__(self, user: Annotated[Employee,Depends(get_current_user)]):
        if self.required_level == user.access_level:
            return user
        elif user.access_level == "admin":
            return user
        elif user.access_level == "editor" and self.required_level == "viewer":
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User does not have enough authority!",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
AdminDependency = Annotated[Employee,Depends(RoleDependency("admin"))]
EditorDependency = Annotated[Employee,Depends(RoleDependency("editor"))]
ViewerDependency = Annotated[Employee,Depends(RoleDependency("viewer"))]