from pydantic import BaseModel

class CreateUser(BaseModel):
    email: str
    password: str
    user_name: str