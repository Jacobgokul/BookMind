"""
User Service Router
Handles user authentication and account management operations.
Includes registration, login, password reset, profile updates, and account deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI core components
from sqlalchemy.orm import Session  # Database session type
from database.database import get_db  # Database session dependency
from database.models import User  # User ORM model
from schemas.user_schema import (  # Pydantic schemas for request/response validation
    CreateUser,
    LoginUser,
    UpdateUser,
    UserResponse
)
from utils.auth_utils import (  # Authentication utility functions
    hash_password,
    verify_password,
    create_jwt_token,
    get_current_user
)

# ========================================
# Router Configuration
# ========================================
router = APIRouter(
    prefix="/user",  # All endpoints start with /user
    tags=["User"]  # Groups endpoints in API documentation
)


# =============================================================
# 🧠 1. REGISTER USER
# =============================================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: CreateUser, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Creates a new user in the database with hashed password.
    Validates that email is unique before registration.
    
    Request Body (CreateUser):
        - user_name: Display name
        - email: Valid email address
        - password: Plain text password (will be hashed)
        
    Returns:
        UserResponse: Created user details (excluding password)
        
    Raises:
        400: Email already registered
    """

    # Check if email already exists in database
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password before storing (never store plain text passwords!)
    hashed_pwd = hash_password(payload.password)
    
    # Create new user instance
    new_user = User(
        user_name=payload.user_name,
        email=payload.email,
        password=hashed_pwd
    )

    # Save to database
    db.add(new_user)  # Stage the new user
    db.commit()  # Commit transaction to database
    db.refresh(new_user)  # Refresh to get auto-generated fields (user_id, timestamps)

    return new_user


# =============================================================
# 🔑 2. LOGIN USER
# =============================================================
@router.post("/login")
def login_user(payload: LoginUser, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    
    Validates credentials and generates a JWT token for authenticated sessions.
    Token should be included in subsequent requests as Bearer token.
    
    Request Body (LoginUser):
        - email: User's email
        - password: Plain text password
        
    Returns:
        dict: Contains access_token and token_type
        
    Raises:
        401: Invalid email or password
    """

    # Find user by email
    user = db.query(User).filter(User.email == payload.email).first()
    
    # Verify user exists and password matches
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token with user_id as payload
    token = create_jwt_token({"user_id": user.user_id})
    
    return {"access_token": token, "token_type": "bearer"}


# =============================================================
# 🔁 3. FORGOT PASSWORD (RESET LINK)
# =============================================================
@router.post("/forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Initiate password reset process.
    
    Generates a reset token that can be used to reset password.
    In production, this token should be sent via email.
    
    Query Parameter:
        - email: User's registered email
        
    Returns:
        dict: Message and reset_token
        
    Raises:
        404: User not found
    """

    # Verify user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate time-limited reset token
    reset_token = create_jwt_token({"email": user.email})
    
    return {"message": "Password reset link sent to email", "reset_token": reset_token}


# =============================================================
# 🔐 4. RESET PASSWORD
# =============================================================
@router.post("/reset_password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Reset user password using reset token.
    
    Uses the token from forgot_password endpoint to update password.
    Token expires after a set time for security.
    
    Query Parameters:
        - token: Reset token from forgot_password
        - new_password: New password to set
        
    Returns:
        dict: Success message
        
    Raises:
        404: Invalid or expired token
    """

    # Verify reset token and extract email
    from utils.auth_utils import verify_reset_token
    email = verify_reset_token(token)
    
    # Find user by email from token
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    # Update password with new hashed password
    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# =============================================================
# 🧑‍💻 5. UPDATE PROFILE
# =============================================================
@router.put("/update_profile", response_model=UserResponse)
def update_profile(
    payload: UpdateUser,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update authenticated user's profile.
    
    Requires JWT token in Authorization header.
    Only updates fields that are provided (partial update).
    
    Request Body (UpdateUser):
        - user_name: New display name (optional)
        - email: New email address (optional)
        - password: New password (optional, will be hashed)
        
    Returns:
        UserResponse: Updated user details
        
    Raises:
        401: Invalid or missing token
    """

    # Fetch user from database (current_user comes from JWT token)
    user = db.query(User).filter(User.user_id == current_user.user_id).first()

    # Update only provided fields
    if payload.user_name:
        user.user_name = payload.user_name
    if payload.email:
        user.email = payload.email
    if payload.password:
        user.password = hash_password(payload.password)

    # Save changes
    db.commit()
    db.refresh(user)  # Refresh to get updated timestamp

    return user


# =============================================================
# ❌ 6. DELETE PROFILE
# =============================================================
@router.delete("/delete_profile")
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete user account.
    
    Requires JWT token in Authorization header.
    This is a hard delete - user data cannot be recovered.
    
    Returns:
        dict: Success message
        
    Raises:
        401: Invalid or missing token
        
    Note: Consider implementing soft delete (is_active=False) in production
    """

    # Hard delete - permanently removes user from database
    db.delete(current_user)
    db.commit() 

    return {"message": "User deleted successfully"}
