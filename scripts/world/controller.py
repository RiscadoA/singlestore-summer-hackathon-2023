from console import Console

from .action import Action, Idle, Walk, Interact

class Controller:
    def prepare(self, world, character_id: str):
        """Called when the controller is assigned to a character"""
        self.world = world
        self.character_id = character_id
        self.character = self.world.characters[character_id]

    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        return Idle()

class HumanController(Controller):
    def __init__(self, console: Console):
        self.console = console
        self.failed = False

    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        if error:
            self.console.print(error)
        
        if not self.console.waiting():
            if self.failed:
                self.console.print("Invalid command, must be one of: walk target, interact item target")
                self.failed = False
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

        self.failed = True
        return Idle(True)