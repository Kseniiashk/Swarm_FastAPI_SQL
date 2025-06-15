from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
        priority=task.priority,
        due_date=task.due_date,
        owner_id=user_id
    )
    for tag_name in task.tags:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_task.tags.append(tag)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).first()


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(
        models.Task.owner_id == user_id
    ).offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None

    db_task.title = task.title
    db_task.description = task.description
    db_task.is_completed = task.is_completed
    db_task.priority = task.priority
    db_task.due_date = task.due_date

    db_task.tags = []
    for tag_name in task.tags:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        db_task.tags.append(tag)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True


def get_task_statistics(db: Session, user_id: int):
    tasks = db.query(models.Task).filter(
        models.Task.owner_id == user_id
    ).order_by(models.Task.priority.asc()).all()
    high_priority = [t for t in tasks if t.priority == 1]
    medium_priority = [t for t in tasks if t.priority == 2]
    low_priority = [t for t in tasks if t.priority == 3]

    completed = sum(1 for t in tasks if t.is_completed)

    return {
        "total_tasks": len(tasks),
        "completed_tasks": completed,
        "pending_tasks": len(tasks) - completed,
        "high_priority_tasks": len(high_priority),
        "tasks_by_priority": {
            "high": {
                "count": len(high_priority),
                "tasks": [{"id": t.id, "title": t.title} for t in high_priority]
            },
            "medium": {
                "count": len(medium_priority),
                "tasks": [{"id": t.id, "title": t.title} for t in medium_priority]
            },
            "low": {
                "count": len(low_priority),
                "tasks": [{"id": t.id, "title": t.title} for t in low_priority]
            }
        },
        "tasks_by_completion": {
            "completed": completed,
            "pending": len(tasks) - completed
        },
        "all_tasks_sorted": [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "is_completed": t.is_completed
            } for t in tasks
        ]
    }