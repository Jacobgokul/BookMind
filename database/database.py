"""
Database Configuration Module
Sets up PostgreSQL connection using SQLAlchemy ORM for database operations.
"""

from sqlalchemy import create_engine  # Engine manages database connection pool
from sqlalchemy.ext.declarative import declarative_base  # Base class for ORM models
from sqlalchemy.orm import sessionmaker  # Factory for creating database sessions


# ========================================
# Database Credentials
# ========================================
# TODO: Move these to environment variables for production security
username = "postgres"
password = "123"
db_name = "bookmind_db"
ip_address = "localhost"
port = 5432

# ========================================
# Database Connection Setup
# ========================================
# Construct PostgreSQL connection string in format: postgresql://user:password@host:port/database
DATABASE_URL = f"postgresql://{username}:{password}@{ip_address}:{port}/{db_name}"

# Create database engine - this manages the connection pool to PostgreSQL
engine = create_engine(DATABASE_URL)

# Test database connection on startup
try:
    engine.connect()
    print("DB Connected")
except:
    print("DB Not connected")


# ========================================
# ORM Setup
# ========================================
# Base class for all model classes - they inherit from this to become database tables
Base = declarative_base()

# Session factory - creates new database sessions for each request
# autoflush=False gives us more control over when changes are sent to the database
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# ========================================
# Dependency Injection
# ========================================
def get_db():
    """
    Database session dependency for FastAPI endpoints.
    Creates a new database session for each request and closes it after use.
    
    Usage in endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()  # Create new session
    try:
        yield db  # Provide session to the endpoint
    finally:
        db.close()  # Ensure session is closed even if an error occurs

