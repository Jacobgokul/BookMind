from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)