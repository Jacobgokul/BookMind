"""
User Schema Module
Defines Pydantic models for request validation and response serialization.

Pydantic schemas:
- Validate incoming request data (type checking, format validation)
- Serialize database models to JSON responses
- Provide automatic API documentation in Swagger/OpenAPI
"""

from pydantic import BaseModel, EmailStr, constr  # Pydantic base model and validators
from typing import Optional  # For optional fields
from datetime import datetime  # For timestamp fields


# ========================================
# Request Schemas (Input Validation)
# ========================================

class CreateUser(BaseModel):
    """
    Schema for user registration request.
    
    Validates user input when creating a new account.
    All fields are required.
    """
    user_name: str  # Display name (any string)
    email: EmailStr  # Validated email format (e.g., user@example.com)
    password: str  # Plain text password (will be hashed before storage)


class LoginUser(BaseModel):
    """
    Schema for user login request.
    
    Validates credentials during authentication.
    Both fields are required.
    """
    email: EmailStr  # User's registered email
    password: str  # User's password


class UpdateUser(BaseModel):
    """
    Schema for profile update request.
    
    All fields are optional - only provided fields will be updated.
    This allows partial updates (e.g., change only email).
    """
    user_name: Optional[str] = None  # New display name (optional)
    email: Optional[EmailStr] = None  # New email address (optional)
    password: Optional[str] = None  # New password (optional)


# ========================================
# Response Schema (Output Serialization)
# ========================================

class UserResponse(BaseModel):
    """
    Schema for user data responses.
    
    Used when returning user information to the client.
    Excludes sensitive data like password.
    
    Config:
        orm_mode: Allows Pydantic to work with SQLAlchemy models
                  Enables response_model in FastAPI endpoints
    """
    user_id: int  # Unique identifier
    user_name: str  # Display name
    email: EmailStr  # Email address
    is_active: bool  # Account status (True = active)
    created_at: datetime  # Registration timestamp
    updated_at: datetime  # Last modification timestamp

    class Config:
        orm_mode = True  # Enable compatibility with SQLAlchemy ORM models
