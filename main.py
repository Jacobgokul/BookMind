from fastapi import FastAPI  # Import FastAPI to create the web application
from database.database import engine, Base  # Import database engine and Base for ORM table creation
from database import models  # Import models to ensure ORM models are registered before table creation

app = FastAPI(title="BookMind")  # Create an instance of FastAPI with a custom title

Base.metadata.create_all(engine)  # Create all database tables defined in models

from routers import user_service, genric_services  # Import routers for user and generic services

# To reflect in UI or to use it the router must register with app (fastapi object).
app.include_router(user_service.router)  # Register user service router with the FastAPI app
app.include_router(genric_services.router)  # Register generic service router with the FastAPI app


@app.get("/")  # Define the root endpoint
def home():
    return "Welcome to BookMind"  # Return a welcome message for the API root

