from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# DB Credentials
username = "postgres"
password = "123"
db_name = "bookmind_db"
ip_address = "localhost"
port = 5432

#configuring db
DATABASE_URL = f"postgresql://{username}:{password}@{ip_address}:{port}/{db_name}"

engine = create_engine(DATABASE_URL)

try:
    engine.connect()
    print("DB COnnected")
except:
    print("DB Not connected")



Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

