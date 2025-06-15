from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Dict

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    priority: int = 0
    due_date: Optional[datetime] = None
    tags: List[str] = []

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str


class PriorityTasks(BaseModel):
    count: int
    tasks: List[dict]


class TasksByCompletion(BaseModel):
    completed: int
    pending: int


class StatsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    high_priority_tasks: int
    tasks_by_priority: Dict[str, PriorityTasks]
    tasks_by_completion: TasksByCompletion
    all_tasks_sorted: List[dict] = []
