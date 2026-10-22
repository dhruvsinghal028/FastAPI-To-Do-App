from fastapi import APIRouter, Depends, HTTPException
from model import Todo
from database import session_local as SessionLocal
from pydantic import BaseModel, Field, typing
from typing import Optional
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user
from passlib.context import CryptContext
from model import user ,Todo    

router = APIRouter(prefix="/user", tags=["user"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")   

# @router.get("/profile", status_code=status.HTTP_200_OK)
# async def get_user_profile(user: user_dependency, db: db_dependency):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
#     return db.query(user).filter(user.id == user.get('user_id')).first()
  
@router.get("/profile", status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: user_dependency, db: db_dependency):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    # Now 'user' correctly points to your imported model!
    # And 'current_user' correctly points to the dictionary.
    user_data = db.query(user).filter(user.id == current_user.get('user_id')).first()
    
    return user_data.__dict__

@router.put("/update_password", status_code=status.HTTP_200_OK)
async def update_password(current_user: user_dependency, db: db_dependency, current_password: str, new_password: str):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    
    user_model = db.query(user).filter(user.id == current_user.get('user_id')).first()
    
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not bcrypt_context.verify(current_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    
    user_model.hashed_password = bcrypt_context.hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}