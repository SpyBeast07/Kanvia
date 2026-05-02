from sqlmodel import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def reset_tasks():
    with engine.connect() as conn:
        print("Dropping task table to reset status column...")
        conn.execute(text("DROP TABLE IF EXISTS task CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS projectcolumn CASCADE;"))
        conn.commit()
        print("Tables dropped.")

if __name__ == "__main__":
    reset_tasks()
