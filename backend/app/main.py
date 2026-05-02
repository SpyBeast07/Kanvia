from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime

from .database import init_db, get_session
from .models import User, Project, Task, ProjectMemberLink
from .schemas import (
    UserCreate, UserRead, ProjectCreate, ProjectRead,
    TaskCreate, TaskRead, TaskUpdate, Token, LoginRequest
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

# --- Project Endpoints ---

@app.post("/api/projects", response_model=ProjectRead)
def create_project(
    project_data: ProjectCreate, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    new_project = Project(name=project_data.name, created_by=current_user.id)
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    
    # Add creator as a member automatically
    member_link = ProjectMemberLink(user_id=current_user.id, project_id=new_project.id)
    session.add(member_link)
    session.commit()
    
    return new_project

@app.get("/api/projects", response_model=List[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get projects where the user is a member
    statement = select(Project).join(ProjectMemberLink).where(ProjectMemberLink.user_id == current_user.id)
    return session.exec(statement).all()

# --- Task Endpoints ---

@app.post("/api/tasks", response_model=TaskRead)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if project exists and user has access (simplified for now)
    project = session.get(Project, task_data.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_task = Task(**task_data.dict())
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
