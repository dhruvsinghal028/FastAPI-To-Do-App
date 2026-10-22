from fastapi import APIRouter, Depends, HTTPException
from model import Todo
from database import session_local as SessionLocal
from pydantic import BaseModel, Field, typing
from typing import Optional
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from .auth import get_current_user

router = APIRouter()

class TodoRequest(BaseModel):
    title : str = Field(min_length=1, max_length=100)   
    description : str = Field(min_length=3, max_length=100)
    priority : int = Field(ge=1, le=5)
    completed : Optional[bool] = Field(default=False)

json_schema_extra = {
    "example": {
        "title": "Buy groceries",
        "description": "Milk, Bread, Eggs",
        "priority": 3,
        "completed": False,
    }
}

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
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    return db.query(Todo).filter(Todo.owner_id == user.get('user_id')).all()

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('user_id')).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@router.post("/todos/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    new_todo = Todo(
        title=todo_request.title,
        description=todo_request.description,
        priority=todo_request.priority,
        completed=todo_request.completed,
        owner_id=user.get('user_id')
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@router.put("/todos/update_todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(user: user_dependency, db: db_dependency, todo_id: int, todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('user_id')).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.completed = todo_request.completed

    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/todos/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('user_id')).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return None