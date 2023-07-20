import logging

from typing import Optional

from .action import Action, Idle, Walk, Interact, Ask
from console import Console

class Controller:
    def prepare(self, world, character_id: str):
        """Called when the controller is assigned to a character"""
        self.world = world
        self.character_id = character_id
        self.character = self.world.characters[character_id]

    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        raise NotImplementedError()

    def answer(self, question: str) -> str:
        """Called when another character asks a question. Should return an answer, or empty string if asker should wait another turn"""
        return "I don't like talking..."

class ScriptedController(Controller):
    def __init__(self, actions = []):
        self.actions = actions
        self.index = 0
    
    def next_action(self, error: str = "") -> Action:
        if error:
            logging.error(error)
        if self.index >= len(self.actions):
            return Idle()
        action = self.actions[self.index]
        self.index += 1
        return action

class HumanController(Controller):
    def __init__(self, console: Console):
        self.console = console
        self.failed = False
        self.ask: Optional[Ask] = None
        self.answering = False

    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        if error:
            self.console.print(error)
            self.ask = None

        if not self.console.waiting():
            if self.failed:
                self.console.print("Invalid command")
                self.failed = False
            elif self.ask is not None:
                self.console.print(self.ask.answer)
                self.ask = None
            self.console.print("- ", end="")

        command = self.console.accept()
        if command is None:
            # Waiting for input
            return Idle(True)

        command = command.split(" ")
        if len(command) == 2 and command[0] == "walk":
            return Walk(command[1])
        elif len(command) == 3 and command[0] == "interact":
            return Interact(command[1], command[2])
        elif len(command) >= 2 and command[0] == "ask":
            self.ask = Ask(command[1], " ".join(command[2:]))
            return self.ask

        self.failed = True
        return Idle(True)

    def answer(self, question: str) -> str:
        """Called when another character asks a question. Should return an answer, or empty string if asker should wait another turn"""
        if not self.answering:
            self.console.clear()
            self.console.print(question)
            self.console.print("- ", end="")
            self.answering = True

        answer = self.console.accept()
        if answer is None:
            return ""
        self.answering = False
        return answer
