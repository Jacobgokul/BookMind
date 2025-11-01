"""
Authentication Utilities Module
Handles password hashing, JWT token generation/validation, and user authentication.

Key Concepts:
- Password Hashing: Converts plain text passwords to secure hashes (one-way encryption)
- JWT (JSON Web Token): Secure token for stateless authentication
- Bearer Token: Standard way to send JWT in HTTP Authorization header
"""

from datetime import datetime, timedelta  # For token expiration
from jose import JWTError, jwt  # Library for JWT encoding/decoding
from fastapi import Depends, HTTPException, status  # FastAPI components
from fastapi.security import HTTPBearer  # Bearer token authentication scheme
from passlib.context import CryptContext  # Password hashing library
from sqlalchemy.orm import Session  # Database session type
from database.database import get_db  # Database dependency
from database.models import User  # User model

# ========================================
# Configuration
# ========================================
SECRET_KEY = "YOUR_SECRET_KEY"  # Used to sign JWT tokens - MUST be kept secret and changed in production
ALGORITHM = "HS256"  # Hashing algorithm for JWT (HMAC SHA-256)
ACCESS_TOKEN_EXPIRE_HOURS = 3  # Token validity duration

# Password hashing context - uses bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer authentication scheme for extracting tokens from headers
security = HTTPBearer()


# ========================================
# Password Helpers
# ========================================
def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Bcrypt is a secure one-way hashing algorithm designed for passwords.
    Same password will produce different hashes due to automatic salting.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password (safe to store in database)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain password matches the hashed version.
    
    Used during login to check if provided password is correct.
    
    Args:
        plain_password: User input password
        hashed_password: Stored hash from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ========================================
# JWT Token Helpers
# ========================================
def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token with expiration time.
    
    JWT contains user data (payload) and is digitally signed to prevent tampering.
    Token should be sent in Authorization header: "Bearer <token>"
    
    Args:
        data: Payload to encode in token (e.g., {"user_id": 123})
        expires_delta: Custom expiration time (optional)
        
    Returns:
        str: Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration time (default or custom)
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})  # Add expiration to payload
    
    # Encode and sign the token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Validates token signature and checks expiration.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded payload from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ========================================
# Password Reset Helpers
# ========================================
def create_reset_token(email: str) -> str:
    """
    Generate a short-lived token for password reset.
    
    Reset tokens expire in 15 minutes for security.
    Should be sent to user's email.
    
    Args:
        email: User's email address
        
    Returns:
        str: Reset token
    """
    expire = datetime.utcnow() + timedelta(minutes=15)  # Short expiration
    to_encode = {"email": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> str:
    """
    Verify password reset token and extract email.
    
    Args:
        token: Reset token from forgot_password endpoint
        
    Returns:
        str: Email address from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("email")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


# ========================================
# Authenticated User Retrieval
# ========================================
def get_current_user(
    token: HTTPBearer = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user.
    
    Extracts JWT token from Authorization header, validates it,
    and returns the corresponding user from database.
    
    Usage in endpoints:
        @app.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return user
    
    Args:
        token: Bearer token from Authorization header
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        401: Invalid token or user not found
    """
    # Decode token and extract payload
    payload = decode_jwt_token(token.credentials)
    user_id: int = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    # Fetch user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user
