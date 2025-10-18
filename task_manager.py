import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Task Manager API")

# Path to JSON file
DB_FILE = Path("tasks_db.json")

# 🧱 Task Model
class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    created_at: datetime = datetime.now()

# 🧠 Utility functions for persistence
def load_tasks() -> List[Task]:
    if DB_FILE.exists():
        with open(DB_FILE, "r") as f:
            try:
                data = json.load(f)
                return [Task(**task) for task in data]
            except json.JSONDecodeError:
                return []
    return []

def save_tasks():
    with open(DB_FILE, "w") as f:
        json.dump([task.dict() for task in tasks], f, indent=4, default=str)

# Load tasks from file at startup
tasks: List[Task] = load_tasks()

# 🟢 Create a task
@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    for existing_task in tasks:
        if existing_task.id == task.id:
            raise HTTPException(status_code=400, detail="Task ID already exists")
    tasks.append(task)
    save_tasks()
    return task

# 🔵 Read all tasks
@app.get("/tasks/", response_model=List[Task])
def get_tasks():
    return tasks

# 🟣 Read one task
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# 🟠 Update a task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks[index] = updated_task
            save_tasks()
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

# 🟥 Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            save_tasks()
            return {"message": f"Task {task_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Task not found")

# 🏠 Root route
@app.get("/")
def home():
    return {"message": "Welcome to Task Manager API! Visit /docs to test endpoints."}
