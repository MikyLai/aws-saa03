import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@localhost:5432/aws_saa03"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass