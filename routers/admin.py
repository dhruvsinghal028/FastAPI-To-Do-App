from fastapi import APIRouter, Depends, HTTPException
from model import Todo
from database import session_local as SessionLocal
from pydantic import BaseModel, Field, typing
from typing import Optional
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from routers import auth, todos,admin
router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if not user or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    if user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
    return db.query(Todo).all()
