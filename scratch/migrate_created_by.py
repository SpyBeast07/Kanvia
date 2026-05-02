import os
import sys

# Add the parent directory to sys.path to import backend modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import text
from app.database import engine

def migrate():
    print("Running migration to add 'created_by' column to 'task' table...")
    with engine.connect() as conn:
        try:
            # Check if column exists first
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='task' AND column_name='created_by'"))
            if not result.fetchone():
                # Get first user ID to use as default for existing tasks
                user_res = conn.execute(text("SELECT id FROM \"user\" LIMIT 1"))
                default_user_id = user_res.fetchone()
                default_id = default_user_id[0] if default_user_id else 1
                
                print(f"Using user ID {default_id} as default for existing tasks.")
                
                # Add column allowing NULL initially
                conn.execute(text(f"ALTER TABLE task ADD COLUMN created_by INTEGER"))
                conn.commit()
                
                # Update existing tasks
                conn.execute(text(f"UPDATE task SET created_by = {default_id}"))
                conn.commit()
                
                # Make it NOT NULL
                conn.execute(text("ALTER TABLE task ALTER COLUMN created_by SET NOT NULL"))
                conn.commit()
                
                # Add foreign key constraint
                conn.execute(text("ALTER TABLE task ADD CONSTRAINT fk_task_creator FOREIGN KEY (created_by) REFERENCES \"user\" (id)"))
                conn.commit()
                
                print("Successfully added 'created_by' column and constraints.")
            else:
                print("Column 'created_by' already exists.")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
