from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime

from .database import init_db, get_session
from .models import User, Project, Task, ProjectMemberLink, UserRole, ProjectColumn
from .schemas import (
    UserCreate, UserRead, ProjectCreate, ProjectRead,
    TaskCreate, TaskRead, TaskUpdate, Token, LoginRequest,
    ProjectColumnCreate, ProjectColumnRead, ProjectColumnUpdate
)
from .auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, check_admin
)

app = FastAPI(title="Kanvia API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# --- Auth Endpoints ---

@app.post("/api/auth/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=Token)
def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == credentials.email)).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/users", response_model=List[UserRead])
def list_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return session.exec(select(User)).all()

# --- Project Endpoints ---

@app.post("/api/projects", response_model=ProjectRead)
def create_project(
    project_data: ProjectCreate, 
    current_user: User = Depends(check_admin),
    session: Session = Depends(get_session)
):
    new_project = Project(name=project_data.name, created_by=current_user.id)
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    
    # Auto-add creator as member
    member_link = ProjectMemberLink(user_id=current_user.id, project_id=new_project.id)
    session.add(member_link)
    session.commit()
    
    # Default columns are now handled by SQLAlchemy event listener in models.py
    
    return new_project

@app.post("/api/projects/{project_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if project exists
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the creator or an admin
    if project.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to add members to this project")
    
    # Check if user exists
    user_to_add = session.get(User, user_id)
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = session.get(ProjectMemberLink, (user_id, project_id))
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    new_member = ProjectMemberLink(user_id=user_id, project_id=project_id)
    session.add(new_member)
    session.commit()
    return {"message": f"User {user_to_add.name} added to project {project.name}"}

@app.get("/api/projects", response_model=List[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role == UserRole.ADMIN:
        return session.exec(select(Project)).all()
    
    # Get projects where the user is a member
    statement = select(Project).join(ProjectMemberLink).where(ProjectMemberLink.user_id == current_user.id)
    return session.exec(statement).all()

@app.get("/api/projects/{project_id}/members", response_model=List[UserRead])
def list_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if user is a member
    membership = session.get(ProjectMemberLink, (current_user.id, project_id))
    if not membership and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to view members of this project")
    
    project = session.get(Project, project_id)
    return project.members

@app.delete("/api/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the creator or an admin
    if project.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    # Manually delete related items if no cascade is configured
    # Delete tasks
    tasks = session.exec(select(Task).where(Task.project_id == project_id)).all()
    for task in tasks:
        session.delete(task)
    
    # Delete columns
    columns = session.exec(select(ProjectColumn).where(ProjectColumn.project_id == project_id)).all()
    for col in columns:
        session.delete(col)
        
    # Delete member links
    links = session.exec(select(ProjectMemberLink).where(ProjectMemberLink.project_id == project_id)).all()
    for link in links:
        session.delete(link)
    
    session.delete(project)
    session.commit()
    return {"message": "Project deleted successfully"}

# --- Column Endpoints ---

@app.get("/api/projects/{project_id}/columns", response_model=List[ProjectColumnRead])
def list_columns(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Admins or members can see columns
    if current_user.role != UserRole.ADMIN:
        member = session.get(ProjectMemberLink, (current_user.id, project_id))
        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this project")
            
    statement = select(ProjectColumn).where(ProjectColumn.project_id == project_id).order_by(ProjectColumn.order)
    return session.exec(statement).all()

@app.post("/api/projects/{project_id}/columns", response_model=ProjectColumnRead)
def create_column(
    project_id: int,
    column_data: ProjectColumnCreate,
    current_user: User = Depends(check_admin),
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # If the requested order is where DONE is, or if we want it "before done"
    # we should shift existing columns.
    # To keep it simple, let's find the current highest order (Done)
    done_col = session.exec(select(ProjectColumn).where(ProjectColumn.project_id == project_id, ProjectColumn.name == "Done")).first()
    
    new_order = column_data.order
    # If adding without specific order, or if adding at/after Done, put it at Done's position and shift Done
    if done_col:
        if new_order >= done_col.order or new_order == 0: # Default to before Done
            new_order = done_col.order
            # Shift Done and any others after new_order
            statement = select(ProjectColumn).where(ProjectColumn.project_id == project_id, ProjectColumn.order >= new_order)
            to_shift = session.exec(statement).all()
            for col in to_shift:
                col.order += 1
                session.add(col)
            
    new_column = ProjectColumn(name=column_data.name, order=new_order, project_id=project_id)
    session.add(new_column)
    session.commit()
    session.refresh(new_column)
    return new_column

@app.patch("/api/columns/{column_id}", response_model=ProjectColumnRead)
def update_column(
    column_id: int,
    column_data: ProjectColumnUpdate,
    current_user: User = Depends(check_admin),
    session: Session = Depends(get_session)
):
    column = session.get(ProjectColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    if column_data.name is not None:
        column.name = column_data.name
    if column_data.order is not None:
        column.order = column_data.order
    
    session.add(column)
    session.commit()
    session.refresh(column)
    return column

@app.delete("/api/columns/{column_id}")
def delete_column(
    column_id: int,
    current_user: User = Depends(check_admin),
    session: Session = Depends(get_session)
):
    column = session.get(ProjectColumn, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    session.delete(column)
    session.commit()
    return {"message": "Column deleted"}

@app.post("/api/tasks", response_model=TaskRead)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if user is a member of the project
    member = session.get(ProjectMemberLink, (current_user.id, task_data.project_id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    new_task = Task(**task_data.dict(), created_by=current_user.id)
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskRead])
def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Admins can see all tasks, others must be members
    if current_user.role != UserRole.ADMIN:
        member = session.get(ProjectMemberLink, (current_user.id, project_id))
        if not member:
            raise HTTPException(status_code=403, detail="Not a member of this project")

    statement = select(Task).where(Task.project_id == project_id)
    return session.exec(statement).all()

@app.patch("/api/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is a member of the project the task belongs to
    member = session.get(ProjectMemberLink, (current_user.id, db_task.project_id))
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Root status endpoint for health checks
@app.get("/api/status")
def get_status():
    return {"backend": "FastAPI", "version": "1.0.0", "status": "operational"}
