import logging

from typing import Optional

from .controller import Controller
from .direction import Direction
from .action import Action, Idle

class Character:
    """Holds the state of a character"""

    def __init__(self, id: str, controller: Controller, position: tuple[int, int], inventory: set[str]):
        self.id = id
        self.controller = controller
        self.position = position
        self.inventory = inventory

        self.action = None
        self.animated_position = tuple(float(x) for x in position)
        self.animated_direction = Direction.SOUTH

    def tick(self, delta_t: float) -> Optional[Action]:
        """Updates the character's state. Returns the new action, if there's any"""
        if self.action is None or self.action.tick(delta_t):
            if self.action is not None:
                if self.action.error:
                    logging.info(f"Character '{self.id}' failed to do {self.action} with error '{self.action.error}'")
                elif not isinstance(self.action, Idle):
                    logging.info(f"Character '{self.id}' finished doing {self.action}")
            self.action = self.controller.next_action(self.action.error if self.action is not None else "")
            if not isinstance(self.action, Idle):
                logging.info(f"Character '{self.id}' is now doing {self.action}")
            return self.action
        return None