from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .models import UserRole

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime

# Project Schemas
class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int
    created_by: int
    created_at: datetime

# Column Schemas
class ProjectColumnBase(BaseModel):
    name: str
    order: int

class ProjectColumnCreate(ProjectColumnBase):
    pass

class ProjectColumnRead(ProjectColumnBase):
    id: int
    project_id: int

class ProjectColumnUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None

# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "MAYBE?"
    is_pinned: bool = False
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    is_pinned: Optional[bool] = None

class TaskRead(TaskBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
