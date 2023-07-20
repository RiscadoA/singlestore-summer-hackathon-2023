import logging
import asyncio

from world import Controller, Action, Idle

from .database import Database
from .prompt import Prompt

class AIController(Controller):
    def __init__(self, db: Database, prompt: Prompt, goal: str, flag: list[bool]):
        self.db = db
        self.prompt = prompt
        self.goal = goal
        self.flag = flag

        self.plan = []
        self.next_action_task = None
        self.just_started = True

    async def async_next_action(self, error: str = "") -> Action:
        if self.flag[0]:
            logging.info(f"'{self.character_id}'s goal '{self.goal}' fulfilled!")
            return Idle()

        if self.just_started:
            self.just_started = False

            self.plan = await self.prompt.plan(
                context=self.db.query(self.goal),
                inventory=self.character.inventory,
                goal=self.goal)
            logging.info(f"'{self.character_id}'s initial plan: {self.plan}")
        else:
            if error:
                self.plan = await self.prompt.reevaluate(
                    context=self.db.query(self.goal, error),
                    memory=self.memory,
                    plan=self.plan,
                    goal=self.goal,
                    error=error)
            else:
                self.plan = await self.prompt.reevaluate(
                    context=self.db.query(self.goal),
                    memory=self.memory,
                    plan=self.plan,
                    goal=self.goal)
            logging.info(f"'{self.character_id}'s new plan: {self.plan}")

        self.memory, action = await self.prompt.execute(
            context=self.db.query(self.plan[0]),
            inventory=self.character.inventory,
            plan=self.plan)
        return action

    def next_action(self, error: str = "") -> Action:
        if self.next_action_task is None:
            self.next_action_task = asyncio.create_task(self.async_next_action(error))

        if self.next_action_task.done():
            result = self.next_action_task.result()
            self.next_action_task = None
            return result
        else:
            return Idle(True)
