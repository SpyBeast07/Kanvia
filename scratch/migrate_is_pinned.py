import os
import sys

# Add the parent directory to sys.path to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import text
from app.database import engine

def migrate():
    print("Running migration to add 'is_pinned' column to 'task' table...")
    with engine.connect() as conn:
        try:
            # Check if column exists first to avoid error if already present
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='task' AND column_name='is_pinned'"))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE task ADD COLUMN is_pinned BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("Successfully added 'is_pinned' column.")
            else:
                print("Column 'is_pinned' already exists.")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
