"""
Database Models Module
Defines ORM models that map Python classes to database tables.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime  # Column types for table definition
from datetime import datetime  # For timestamp fields
from .database import Base  # Base class that makes this a database model


class User(Base):
    """
    User Model - Represents the 'users' table in the database.
    
    This class defines the structure of the users table and maps each attribute
    to a database column. SQLAlchemy handles the conversion between Python objects
    and database rows.
    
    Table Structure:
        - user_id: Primary key, auto-increments for each new user
        - email: User's email address (required, unique in practice)
        - password: Hashed password (never store plain text!)
        - user_name: Display name for the user
        - is_active: Soft delete flag (True = active, False = deactivated)
        - created_at: Timestamp when user registered
        - updated_at: Timestamp when user profile was last modified
    """
    __tablename__ = "users"  # Name of the table in the database
    __table_args__ = {"extend_existing": True}  # Allows model redefinition without errors

    # Primary Key - Unique identifier for each user
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User Credentials and Profile
    email = Column(String, nullable=False)  # Email cannot be empty
    password = Column(String, nullable=False)  # Stores hashed password
    user_name = Column(String, nullable=False)  # Display name
    
    # Account Status
    is_active = Column(Boolean, default=True)  # Default to active when user registers
    
    # Timestamps - Automatically managed by SQLAlchemy
    created_at = Column(DateTime, default=datetime.utcnow)  # Set once on creation
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Auto-updates on modification