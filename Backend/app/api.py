import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from main import Priority, Status, Task, TaskList, Application, TaskListModel, TaskModel

DATABASE_PATH = os.path.join(os.getcwd(), "Vaults", "todovault.db")
app = FastAPI()
app.db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
app.application = Application(app.db)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_application():
    return app.application

@app.post("/lists", response_model= TaskListModel)
def create_list(task_list_model: TaskListModel, application: Application = Depends(get_application)):
    
    task_list: TaskList = application.create_new_list(task_list_model.name)
    return TaskListModel(id= task_list.list_id, name=task_list.name)
    
@app.post("/lists/{list_id}/tasks", response_model= TaskModel)
def create_task_in_list(list_id: str, task_model: TaskModel, application: Application = Depends(get_application)):
    task: Task = application.create_new_task(list_id, task_model.model_dump())
    return TaskModel(id=task.task_id, name=task.name, description=task.description, priority=task.priority, status=task.status, list_id=task.list_id)

@app.get("/lists", response_model= List[TaskListModel])
def get_lists(application: Application = Depends(get_application)):
    task_lists: list[TaskList] = application.show_all_lists()
    return [TaskListModel(id= task_list.list_id, name=task_list.name) for task_list in task_lists]

@app.get("/lists/{list_id}/tasks", response_model= List[TaskModel])
def get_task_in_list(list_id: str, application: Application = Depends(get_application)):
    tasks: list[Task] = application.print_all_todos_per_list(list_id)
    return [TaskModel(id = task.task_id, name=task.name, description=task.description, priority=task.priority, status=task.status, list_id=task.list_id) for task in tasks]

@app.get("/lists/{list_id}/tasks/{task_id}", response_model= TaskModel)
def get_task(list_id: str, task_id: str, application: Application = Depends(get_application)):
    task: Task = application.load_task(task_id)
    if task:
        return TaskModel(id = task.task_id, name=task.name, description=task.description, priority=task.priority, status=task.status, list_id=task.list_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/lists/{list_id}/tasks/{task_id}/name", response_model= TaskModel)
def update_task_name(list_id: str, task_id: str, new_name: str, application: Application = Depends(get_application)):
    task = application.load_task(task_id)
    if task:
        updated_task: Task = task.update_name(new_name)
        return TaskModel(id = updated_task.task_id, name=updated_task.name, description=updated_task.description, priority=updated_task.priority, status=updated_task.status, list_id=updated_task.list_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/lists/{list_id}/tasks/{task_id}/description", response_model= TaskModel)
def update_task_description(list_id: str, task_id: str, new_description: str, application: Application = Depends(get_application)):
    task = application.load_task(task_id)
    if task:
        updated_task: Task = task.update_description(new_description)
        return TaskModel(id = updated_task.task_id, name=updated_task.name, description=updated_task.description, priority=updated_task.priority, status=updated_task.status, list_id=updated_task.list_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/lists/{list_id}/tasks/{task_id}/priority", response_model= TaskModel)
def update_task_priority(list_id: str, task_id: str, new_priority: int, application: Application = Depends(get_application)):
    task = application.load_task(task_id)
    if task:
        updated_task: Task = task.update_priority(Priority(new_priority))
        return TaskModel(id = updated_task.task_id, name=updated_task.name, description=updated_task.description, priority=updated_task.priority, status=updated_task.status, list_id=updated_task.list_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/lists/{list_id}/tasks/{task_id}/status", response_model= TaskModel)
def update_task_status(list_id: str, task_id: str, new_status: int, application: Application = Depends(get_application)):
    task = application.load_task(task_id)
    if task:
        updated_task: Task = task.update_status(Status(new_status))
        return TaskModel(id = updated_task.task_id, name=updated_task.name, description=updated_task.description, priority=updated_task.priority, status=updated_task.status, list_id=updated_task.list_id)
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/lists/{list_id}/tasks/{task_id}")
def delete_task(list_id: str, task_id: str, application: Application = Depends(get_application)):
    list = application.load_tasklist(list_id)
    task = application.load_task(task_id)
    if task:
        application.load_tasklist(task.list_id).delete_task(task_id)
        return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/lists/{list_id}")
def delete_list(list_id: str, application: Application = Depends(get_application)):
    application.delete_list(list_id)
    return {"message": "List deleted successfully"}

