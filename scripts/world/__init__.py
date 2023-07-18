from typing import Optional

from .interaction import Interaction
from .object import Object
from .character import Character, Direction
from .action import Action, Idle, Walk, Interact
from .navigator import Navigator
from .controller import Controller, HumanController

class World:
    """Holds all of the state of the world"""

    def __init__(self, size: tuple[int, int]):
        self.size = size

        self.characters = {}
        self.objects = {}
        self.navigator = Navigator(size, self.objects)

    def add_character(self, id: str, controller: Controller, position: tuple[int, int], inventory: set[str] = set()):
        """Adds a new character to the world"""
        assert id not in self.characters, f"Character with id {id} already exists"
        self.characters[id] = Character(controller, position, inventory)
        controller.prepare(self, id)

    def add_object(self, id: str, position: tuple[int, int], interaction: Optional[Interaction] = None):
        """Adds a new object to the world at the given position, optionally with an interaction"""
        assert id not in self.objects, f"Object with id {id} already exists"
        self.objects[id] = Object(position, interaction)

    def tick(self, delta_t: float):
        """Updates the state of all characters in the world"""
        for id, character in self.characters.items():
            action = character.tick(delta_t)
            if action is not None:
                action.prepare(self, id)
