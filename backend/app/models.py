from typing import List, Optional
from datetime import datetime
from enum import Enum
from sqlmodel import Field, Relationship, SQLModel

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class ProjectMemberLink(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: UserRole = Field(default=UserRole.MEMBER)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    projects_created: List["Project"] = Relationship(back_populates="creator")
    projects: List["Project"] = Relationship(back_populates="members", link_model=ProjectMemberLink)
    assigned_tasks: List["Task"] = Relationship(back_populates="assignee", sa_relationship_kwargs={"foreign_keys": "Task.assigned_to"})
    created_tasks: List["Task"] = Relationship(back_populates="creator", sa_relationship_kwargs={"foreign_keys": "Task.created_by"})

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    creator: User = Relationship(back_populates="projects_created")
    members: List[User] = Relationship(back_populates="projects", link_model=ProjectMemberLink)
    tasks: List["Task"] = Relationship(back_populates="project")
    columns: List["ProjectColumn"] = Relationship(back_populates="project")

class ProjectColumn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    order: int = Field(default=0)
    project_id: int = Field(foreign_key="project.id")
    
    project: Project = Relationship(back_populates="columns")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="MAYBE?")
    is_pinned: bool = Field(default=False)
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    created_by: int = Field(foreign_key="user.id")
    project_id: int = Field(foreign_key="project.id")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    project: Project = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(sa_relationship_kwargs={"foreign_keys": "Task.assigned_to"})
    creator: User = Relationship(sa_relationship_kwargs={"foreign_keys": "Task.created_by"})
