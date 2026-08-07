from fastapi import APIRouter, HTTPException
from services.task_service import TaskService, Task
from typing import List

router = APIRouter()
task_service = TaskService()

@router.get("/", response_model=List[Task])
def get_tasks():
    return task_service.get_all_tasks()

@router.post("/", response_model=Task)
def create_task(task: Task):
    return task_service.create_task(task)

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task: Task):
    updated = task_service.update_task(task_id, task.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@router.delete("/{task_id}")
def delete_task(task_id: int):
    success = task_service.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
