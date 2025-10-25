from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from schemas.user_schema import (
    CreateUser,
    LoginUser,
    UpdateUser,
    UserResponse
)
from utils.auth_utils import (
    hash_password,
    verify_password,
    create_jwt_token,
    get_current_user
)

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


# =============================================================
# 🧠 1. REGISTER USER
# =============================================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: CreateUser, db: Session = Depends(get_db)):
    """
    ### Create (Register) User
    Creates a new user in the **users** table.

    **Model Table:** `User`  
    **Request Schema:** `CreateUser`  
    **Response Schema:** `UserResponse`

    **Process:**
    - Validates if the email already exists  
    - Hashes the password before saving  
    - Inserts new user record in the DB
    """

    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pwd = hash_password(payload.password)
    new_user = User(
        user_name=payload.user_name,
        email=payload.email,
        password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =============================================================
# 🔑 2. LOGIN USER
# =============================================================
@router.post("/login")
def login_user(payload: LoginUser, db: Session = Depends(get_db)):
    """
    ### Login User
    Authenticates user credentials and returns a JWT access token.

    **Model Table:** `User`  
    **Request Schema:** `LoginUser`

    **Process:**
    - Finds user by email  
    - Verifies password using hashing  
    - Generates and returns JWT token if valid
    """

    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_jwt_token({"user_id": user.user_id})
    return {"access_token": token, "token_type": "bearer"}


# =============================================================
# 🔁 3. FORGOT PASSWORD (RESET LINK)
# =============================================================
@router.post("/forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    ### Forgot Password
    Initiates a password reset by generating a reset token.

    **Model Table:** `User`

    **Process:**
    - Checks if the email exists  
    - Generates a reset token (to be sent via email)
    """

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    reset_token = create_jwt_token({"email": user.email})
    # (Optional) send email logic can be added here
    return {"message": "Password reset link sent to email", "reset_token": reset_token}


# =============================================================
# 🔐 4. RESET PASSWORD
# =============================================================
@router.post("/reset_password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    ### Reset Password
    Resets user password using a valid reset token.

    **Model Table:** `User`

    **Process:**
    - Decodes reset token to extract email  
    - Updates password hash in the database
    """

    from utils.auth_utils import verify_reset_token
    email = verify_reset_token(token)
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

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
    ### Update Profile
    Allows the logged-in user to modify their profile details.

    **Model Table:** `User`  
    **Request Schema:** `UpdateUser`  
    **Response Schema:** `UserResponse`

    **Process:**
    - Authenticates user via JWT  
    - Updates provided fields only
    """

    user = db.query(User).filter(User.user_id == current_user.user_id).first()

    if payload.user_name:
        user.user_name = payload.user_name
    if payload.email:
        user.email = payload.email
    if payload.password:
        user.password = hash_password(payload.password)

    db.commit()
    db.refresh(user)

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
    ### Delete Profile
    Permanently deletes the logged-in user's account.

    **Model Table:** `User`

    **Process:**
    - Authenticates user via JWT  
    - Removes their record from the users table
    """

    db.delete(current_user) #hard delete
    db.commit() 

    return {"message": "User deleted successfully"}
