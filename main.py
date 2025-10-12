from fastapi import FastAPI
from database.database import engine, Base
from database import models

app = FastAPI(title="BookMind")

Base.metadata.create_all(engine)

from routers import user_service

app.include_router(user_service.router)


@app.get("/")
def home():
    return "Welcome to BookMind"

