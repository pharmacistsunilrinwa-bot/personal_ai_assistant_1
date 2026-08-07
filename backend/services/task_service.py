import json
import os
from typing import List, Dict, Optional
from pydantic import BaseModel

class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    status: str = "pending"  # pending, in_progress, completed
    due_date: Optional[str] = None
    project: Optional[str] = "Personal"

class TaskService:
    def __init__(self, db_path='tasks.json'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump([], f)

    def _load_tasks(self) -> List[Dict]:
        with open(self.db_path, 'r') as f:
            return json.load(f)

    def _save_tasks(self, tasks: List[Dict]):
        with open(self.db_path, 'w') as f:
            json.dump(tasks, f, indent=4)

    def get_all_tasks(self) -> List[Dict]:
        return self._load_tasks()

    def create_task(self, task: Task) -> Dict:
        tasks = self._load_tasks()
        task_id = max([t['id'] for t in tasks], default=0) + 1
        new_task = task.dict()
        new_task['id'] = task_id
        tasks.append(new_task)
        self._save_tasks(tasks)
        return new_task

    def update_task(self, task_id: int, updated_fields: Dict) -> Optional[Dict]:
        tasks = self._load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task.update({k: v for k, v in updated_fields.items() if v is not None})
                self._save_tasks(tasks)
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        tasks = self._load_tasks()
        initial_len = len(tasks)
        tasks = [t for t in tasks if t['id'] != task_id]
        if len(tasks) < initial_len:
            self._save_tasks(tasks)
            return True
        return False
