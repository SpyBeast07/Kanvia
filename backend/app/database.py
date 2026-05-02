import os
from dotenv import load_dotenv, find_dotenv
from sqlmodel import create_engine, Session, SQLModel

# Load .env file
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
