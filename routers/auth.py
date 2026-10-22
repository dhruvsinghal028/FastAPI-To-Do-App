from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from model import user
from passlib.context import CryptContext
from database import session_local as SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import secrets
from datetime import timedelta, datetime, timezone


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = secrets.token_urlsafe(64)
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")    
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token") 


class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class token_response(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user_model = db.query(user).filter(user.username == username).first()
    if not user_model:
        return False
    if not bcrypt_context.verify(password, user_model.hashed_password):
        return False
    return user_model

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "user_id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return  {"username": username, "user_id": user_id, "user_role": user_role}
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: UserCreate ):
    # # Debug print for password
    # print(f"Password value: {create_user_request.password}")
    # print(f"Password length: {len(create_user_request.password)}")
    create_user_model = user(
        username=create_user_request.username,  
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),  
        role=create_user_request.role,
        is_active=True
        )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/token", response_model=token_response)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user_authenticated = authenticate_user(form_data.username, form_data.password, db)
    if not user_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(user_authenticated.username, user_authenticated.id,user_authenticated.role, timedelta(minutes=20))
    return token_response(access_token=token, token_type="bearer")