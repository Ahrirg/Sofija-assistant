import os
import datetime

from ..utils.Logging import log
from dataclasses import dataclass

@dataclass
class Task():
    id: int
    status: str
    task: str
    TimeToComplete: str | None

class Todoapp():
    # Format:
    # id: | status: | Task: | TimeToComplete: 
    def __init__(self, path: str):
        if not os.path.exists(path):
            with open(path, "a+") as f: 
                pass
        self.file = path
        self.Tasks: list[Task] = self.parse_rows()

    def cleanup(self):
        file_content = ""
        with open(self.file, "r") as f:
            for line in f:
                if line.replace(" ", "") != "":
                    continue
                file_content += f"{line}\n"
        
        with open(self.file, "w") as f:
            f.write(file_content)

    def override_file(self) -> None:
        string = ""

        for task in self.Tasks:
            string += f"\n{task.id} <|sidewall|> {task.status} <|sidewall|> {task.task} <|sidewall|> {task.TimeToComplete}"

        with open(self.file, "w") as f:
            f.write(string)

    def add_row(self, task: Task) -> None:
        with open(self.file, "a") as f:
            f.write(f"\n{task.id} <|sidewall|> {task.status} <|sidewall|> {task.task} <|sidewall|> {task.TimeToComplete}")

    def _parse_row(self, raw_data: str) -> Task | None:
        split_data = raw_data.split("<|sidewall|>")
        split_data = [part.strip() for part in split_data]
        if len(split_data) != 4:
            log(raw_data)
            return None

        try:
            id = int(split_data[0])
        except Exception as e:
            log(f"failed to parse id in '{raw_data}' string")
            return None

        status = split_data[1]
        task = split_data[2]
        time = split_data[3]

        task = Task(
            id=id,
            status=status,
            task=task,
            TimeToComplete=time
        )
        return task

    def parse_rows(self) -> list[Task]:
        tasks: list[Task] = []

        with open(self.file, "r") as f:
            for line in f:
                cur_task = self._parse_row(line)
                if cur_task:
                    tasks.append(cur_task)

        return tasks

    def _find_task(self, id: int) -> Task | None:
        for task in self.Tasks:
            if task.id == id:
                return task

        return None

    def remove_row(self, id: int): 
        cur_task = self._find_task(id)
        if not cur_task:
            return False
        self.Tasks.remove(cur_task)
        self.override_file()
        return True

    def change_status(self, id: int, new_status: str):
        cur_task = self._find_task(id)
        if cur_task:
            cur_task.status = new_status
            self.override_file()

    def _max_id(self):
        max_id = 0
        for task in self.Tasks:
            if task.id > max_id:
                max_id = task.id
        return max_id

def add_task(task: str, time: str) -> str:
    Todo = Todoapp(os.environ.get("TODO_FILE_PATH", "./todos.txt"))
    new_id = Todo._max_id() + 1
    Todo.add_row(Task(
        id = new_id,
        status = "Not done",
        task = task,
        TimeToComplete = time
    ))

    return f"New task (id: {new_id}) created"

def update_task_status(id: str, status: str):
    try:
        id_int = int(id)
    except:
        return "There was error trying to parse int from id, please provide valid id"
    
    Todo = Todoapp(os.environ.get("TODO_FILE_PATH", "./todos.txt"))
    Todo.change_status(id_int, status)

    return "Task status successufully changed"

def get_tasks() -> str:
    Todo = Todoapp(os.environ.get("TODO_FILE_PATH", "./todos.txt"))
    prompt = "".join(
        "id | status | task | deadline\n"
        "-----------------------------------------"
    )
    for task in Todo.Tasks:
        prompt += f"\n{task.id} | {task.status} | {task.task} | {task.TimeToComplete}"

    return prompt

def get_tool_usage_prompt() -> str:
    return "".join(
        'Tool for managing user todos, each todo has status which can be ["todo", "completed", "deleted"] any task marked as completed or deleted will be automaticly destroyed after 24 hours.\n'
        "'tool:get_tasks()' can be used to get all current tasks in a table (id: | status: | task: | deadline: ) . Example usage 'tool:get_tasks()'"
        "'tool:add_task(task: str, deadline: str | None)' can be used to add new task to todos, task parameter is manditory and description what is needed to do, deadline is optional parameter meant to give deadline to task. Example usage 'tool:add_task('finish homework', '2025-11-10')'\n"
        "'tool:update_task_status(id: int, status: str)' can be used to change status or delete old tasks. id is the tasks id, status is the new status of the task, must be one of these ['todo', 'completed', 'deleted'] if task status is not 'todo' will be deleted after 24 hours. Example usage 'tool:update_task_status(2, 'completed')'\n"
    )

def get_tools() -> list[dict]:
    return [
        {"command": "get_tasks", "args": "", "func": get_tasks},
        {"command": "add_task", "args": "str, str_opt", "func": add_task},
        {"command": "update_task_status", "args": "int, status", "func": update_task_status}
    ]
