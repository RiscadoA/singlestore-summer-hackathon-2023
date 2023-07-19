import logging

from world import Controller, Action, Idle

from .database import Database
from .prompt import Prompt

class AIController(Controller):
    def __init__(self, db: Database, prompt: Prompt, goal: str, flag: list[bool]):
        self.db = db
        self.prompt = prompt
        self.goal = goal
        self.flag = flag

        self.tasks = [goal]
        self.previous_task = None
        self.previous_action = None
    
    def fix(self, task: str, action: Action, error: str, exhausted: bool = False):
        logging.info(f"'{self.character_id}' fixing task '{task}' which was executed with '{action}', which caused the error '{error}'")

        context = self.db.query(task, error)
        inventory = self.character.inventory
        logging.info(f"'{self.character_id}'s context: {context}")
        logging.info(f"'{self.character_id}'s inventory: {inventory}") 

        new_tasks = self.prompt.fix(context, inventory, task, action, error, exhausted)
        self.tasks = new_tasks + self.tasks
        logging.info(f"'{self.character_id}'s new tasks: {self.tasks}")

    def execute(self, task: str) -> Action:
        logging.info(f"'{self.character_id}' executing task '{task}'")

        context = self.db.query(task)
        inventory = self.character.inventory
        logging.info(f"'{self.character_id}'s context: {context}")
        logging.info(f"'{self.character_id}'s inventory: {inventory}")

        return self.prompt.execute(context, inventory, task)

    def exhausted(self, action: Action):
        logging.info(f"'{self.character_id}' exhausted all tasks but goal '{self.goal}' was not fulfilled!")
        self.fix(self.goal, action, "No more tasks to execute, but goal was not fulfilled!", True)

    def next_action(self, error: str = "") -> Action:
        if error:
            assert self.previous_task is not None
            assert self.previous_action is not None
            self.fix(self.previous_task, self.previous_action, error)
            return Idle(True)
        elif self.tasks:
            task = self.tasks.pop(0)
            action = self.execute(task)
            self.previous_task = task
            self.previous_action = action
            return action
        elif self.flag[0]:
            logging.info(f"'{self.character_id}'s goal '{self.goal}' fulfilled!")
            return Idle()
        else:
            assert self.previous_action is not None
            self.exhausted(self.previous_action)
            return Idle(True)

