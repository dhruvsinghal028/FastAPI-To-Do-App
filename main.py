from fastapi import FastAPI, Depends, HTTPException
from database import engine, appBase
from routers import auth, users, todos, admin
import model

app = FastAPI()

model.appBase.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
