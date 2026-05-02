from sqlmodel import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def reset_db():
    with engine.connect() as conn:
        print("Dropping all tables...")
        conn.execute(text("DROP TABLE IF EXISTS task CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS projectcolumn CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS projectmemberlink CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS project CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE;"))
        conn.commit()
        print("Tables dropped.")

if __name__ == "__main__":
    reset_db()
