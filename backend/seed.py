from sqlmodel import Session, create_engine, select
from app.models import User, Project, ProjectMemberLink, Task, UserRole
from app.auth import get_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def seed():
    with Session(engine) as session:
        # 1. Create Admin User
        admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print(f"Created Admin: {admin.email}")
        
        # 1b. Create Member1 User
        member1 = session.exec(select(User).where(User.email == "mem1@example.com")).first()
        if not member1:
            member1 = User(
                name="Member1",
                email="mem1@example.com",
                password_hash=get_password_hash("mem1123"),
                role=UserRole.MEMBER
            )
            session.add(member1)
            session.commit()
            session.refresh(member1)
            print(f"Created Member1: {member1.email}")
        
        # 2. Create Project
        project = session.exec(select(Project).where(Project.name == "Kanvia Playground")).first()
        if not project:
            project = Project(name="Kanvia Playground", created_by=admin.id)
            session.add(project)
            session.commit()
            session.refresh(project)
            print(f"Created Project: {project.name}")
            
            # Add Admin as member
            member = ProjectMemberLink(user_id=admin.id, project_id=project.id)
            session.add(member)
            session.commit()

        # 3. Create initial tasks if empty
        existing_tasks = session.exec(select(Task).where(Task.project_id == project.id)).all()
        if not existing_tasks:
            tasks = [
                Task(title="First, rename this card", status="IN_PROGRESS", project_id=project.id, assigned_to=admin.id),
                Task(title="Second, move this card to NOT NOW", status="IN_PROGRESS", project_id=project.id, assigned_to=admin.id),
                Task(title="Implement Drag & Drop", status="TODO", project_id=project.id, assigned_to=admin.id),
            ]
            session.add_all(tasks)
            session.commit()
            print("Seeded initial tasks.")

if __name__ == "__main__":
    seed()
    print("Seeding complete!")
