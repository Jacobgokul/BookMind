from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from schemas.user_schema import CreateUser

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

"""
TODO:
    - Register API -> Create
    - Login API -> Read
    - Forgot password -> Edit
    - Update profile -> Edit
    - Delete profile -> Delete
"""

@router.post("/user_register")
def create_user(payload: CreateUser, db: Session = Depends(get_db)):

    # create user in user table
    user_record = User(
        user_name = payload.user_name,
        email = payload.email,
        password = payload.password
    )

    db.add(user_record)

    db.commit()

    return "User created successfully"