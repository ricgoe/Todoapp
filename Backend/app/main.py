from enum import Enum
import uuid
import os
import sqlite3
from typing import Optional, List
from pydantic import BaseModel

class Priority(Enum):
    NO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Status(Enum):
    TODO = 0
    IN_PROGRESS = 1
    DONE = 2

class TaskModel(BaseModel):
    id : Optional[str] = None
    name: str
    description: Optional[str] = ""
    priority: Optional[Priority] = 0
    status: Optional[Status] = 0
    list_id: Optional[str] = None

class TaskListModel(BaseModel):
    id: Optional[str] = None
    name: str

class TaskList:
    def __init__(self, list_id: str, name: str, db_connection) -> None:
        """
        Initializes a new instance of the TaskList class.

        Parameters:
            list_id (str): The ID of the task list.
            name (str): The name of the task list.
        """
        self.name = name
        self.list_id = list_id
        self.dbconnection: sqlite3.Connection = db_connection
        self.cursor = self.dbconnection.cursor()
        
    @classmethod
    def new_list(cls, name: str, db_connection) -> "TaskList":
        """
        Creates a new TaskList object with a randomly generated UUID and the given name.

        Parameters:
            name (str): The name of the TaskList.

        Returns:
            TaskList: A new TaskList object with the generated UUID and the given name.
        """
        
        list_uuid = str(uuid.uuid4())
        return cls(list_uuid, name=name, db_connection=db_connection)

    def update_list_name(self, new_name: str) -> None:
        self.name = new_name
        self.cursor.execute("UPDATE tasklists SET name = ? WHERE id = ?", (self.name, self.list_id))
        self.dbconnection.commit()

        
    def delete_task(self, task_id) -> None:
        if isinstance(task_id, tuple):
            task_id = task_id[0]
            
        self.cursor.execute("SELECT name FROM tasklists WHERE id = ?", (task_id,)).fetchone()
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.dbconnection.commit()


class Task:
    def __init__(self, task_id: int, name: str, description: str, priority: Priority, status: Status, list_id: str, db_connection) -> None:
        self.task_id = task_id
        self.name = name
        self.description = description
        self.priority = priority
        self.status = status
        self.dbconnection: sqlite3.Connection = db_connection
        self.list_id = list_id
        
    
    @classmethod
    def new_task(cls, name: str, description: str, db_connection, priority: Priority = Priority.NO, status = Status.TODO, list_id: str = None) -> "Task":
        """
        Creates a new Task object with a randomly generated UUID and the given name, description, priority, and status.

        Parameters:
            name: A string representing the name of the task.
            description: A string representing the description of the task.
            priority: An optional Priority object representing the priority of the task. Defaults to Priority.NO.
            status: An optional Status object representing the status of the task. Defaults to Status.TODO.
        
        Returns:
            A new Task object with the generated UUID and the given name, description, priority, and status.
        """
        task_id = str(uuid.uuid4())
        return cls(task_id, name, description, db_connection=db_connection, priority=priority, status=status, list_id=list_id)
    
    
    def update_name(self, new_name: str) -> 'Task':
        """
        Updates the name of the task with a new name entered by the user.
        """
        self.name = new_name
        self.dbconnection.execute("UPDATE tasks SET name = ? WHERE id = ?", (self.name, self.task_id))
        self.dbconnection.commit()
        return self
    
    def update_description(self, new_description: str) -> 'Task':
        """
        Updates the description of the task with a new description entered by the user.
        """
        self.description = new_description
        self.dbconnection.execute("UPDATE tasks SET description = ? WHERE id = ?", (self.description, self.task_id))
        self.dbconnection.commit()
        return self
    
    def update_priority(self, new_priority: Priority) -> 'Task':
        """
        Updates the priority of the task with a new priority entered by the user.
        """
        self.priority = new_priority
        self.dbconnection.execute("UPDATE tasks SET priority = ? WHERE id = ?", (self.priority.value, self.task_id))
        self.dbconnection.commit()
        return self
    
        
    
    def update_status(self, new_status: Status) -> 'Task':
        """
        Updates the status of the task with a new status input by the user.
        """
        self.status = new_status
        self.dbconnection.execute("UPDATE tasks SET status = ? WHERE id = ?", (self.status.value, self.task_id))
        self.dbconnection.commit()
        return self
    

class User:
    def __init__(self, user_id: int, name: str, password: str) -> None:
        self.user_id = user_id
        self.name = name
        self.password = password


class Application:
    def __init__(self, db: sqlite3.Connection) -> None:
        """
        Initializes the Application object by setting up choice dictionaries, vault, and new_list to default values.
        """
        
        self.vault_path = os.path.join(os.getcwd(), "Vaults")
        if not os.path.exists(self.vault_path):
            os.makedirs(self.vault_path)
            
        self.dbconnection = db
        self.cursor: sqlite3.Cursor = self.dbconnection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasklists (id TEXT PRIMARY KEY, name TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, priority INTEGER, status INTEGER, list_id TEXT, FOREIGN KEY(list_id) REFERENCES tasklists(id));")
        self.cursor.execute("PRAGMA encoding = 'CP1252';")
        self.dbconnection.commit()
        self.new_list = None
        self.saved = False
    

    def create_new_task(self, list_id: str, task: dict):
        name = task['name']
        if not name:
            return
        task_obj: Task = Task.new_task(name, task['description'], priority=Priority(task['priority']), status=Status(task['status']), list_id=list_id, db_connection=self.dbconnection)
        self.cursor.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)", (task_obj.task_id, task_obj.name, task_obj.description, task_obj.priority.value, task_obj.status.value, task_obj.list_id))
        self.dbconnection.commit()
        return task_obj


    def create_new_list(self, list_name: str) -> TaskList:
        if not list_name:
            return
        new_list: TaskList = TaskList.new_list(list_name, db_connection=self.dbconnection)
        
        self.cursor.execute("INSERT INTO tasklists VALUES (?, ?)", (new_list.list_id, new_list.name))
        self.dbconnection.commit()
        return new_list

    def _is_populated(self, **kwargs) -> bool:
        mode = kwargs.get("list_id", None)
        if not mode:
            return self.cursor.execute("SELECT COUNT(*) FROM tasklists").fetchone()[0] > 0
        else:
            return self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE list_id = ?", (mode,)).fetchone()[0] > 0
         
    def show_all_lists(self) -> List[TaskListModel]:
        if self._is_populated():
            self.cursor.execute("SELECT id, name FROM tasklists")
            return [TaskList(list_id= row[0], name = row[1], db_connection=self.dbconnection) for row in self.cursor.fetchall()]
        else:
            return []

    def print_all_todos_per_list(self, list_id) -> List[TaskModel]:      
        if self._is_populated(list_id=list_id):
            self.cursor.execute("SELECT id, name, description, status, priority FROM tasks WHERE list_id = ?", (list_id,))
            return [Task(id = row[0], name = row[1], description = row[2] if row[2] else "", status = Status(row[3]).value, priority = Priority(row[4]).value, list_id = list_id, db_connection=self.dbconnection) for row in self.cursor.fetchall()]
        else:
            return []
              
    def get_task_id(self, list_id) -> str:
        tasks = self.print_all_todos_per_list(list_id)
        if not tasks:
            return None
        if len(tasks) == 1:
            return tasks[0]["id"]
        return None
              
    def get_list_id(self) -> str:
        lists = self.show_all_lists()
        if not lists:
            return None
        if len(lists) == 1:
            return lists[0]["id"]
        else: 
            return None
        
    def load_tasklist(self, list_id):
        self.cursor.execute("SELECT id, name FROM tasklists WHERE id = ?", (list_id,))
        row = self.cursor.fetchone()
        if row:
            return TaskList(row[0], row[1], self.dbconnection)
        else:
            return None

    def load_task(self, task_id):
        self.cursor.execute("SELECT id, name, description, priority, status, list_id FROM tasks WHERE id = ?", (task_id,))
        row = self.cursor.fetchone()
        if row:
            return Task(row[0], row[1], row[2], Priority(int(row[3])), Status(int(row[4])), list_id=row[5], db_connection=self.dbconnection)
        return None
    
    
    def delete_list(self, list_id: str) -> None:
        if list_id:
            list_name = self.cursor.execute("SELECT name FROM tasklists WHERE id = ?", (list_id,)).fetchone()[0]
            self.cursor.execute("DELETE FROM tasklists WHERE id = ?", (list_id,))
            self.cursor.execute("DELETE FROM tasks WHERE list_id = ?", (list_id,))
            self.dbconnection.commit()
        

    def close_app(self) -> None:
        self.dbconnection.close()
        
