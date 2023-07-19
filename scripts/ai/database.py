from typing import Optional
from world import World

class Database():
    """Interface for the database which stores the context used by the AI.
    The context includes:
    - rules;
    - objects;
    - characters.
    """

    def fill(self, world: World):
        """Fills the database with data from the given world"""
        raise NotImplementedError()

    def query(self, task: str, error: Optional[str] = None) -> list[str]:
        """Queries context for the given task, optionally with the error message of the previous action if it failed"""
        raise NotImplementedError()

class DumbDatabase(Database):
    """Dumb database which dumps all of the context to the AI"""

    def __init__(self):
        self.world = None

    def fill(self, world: World):
        self.world = world

    def query(self, task: str, error: Optional[str] = None) -> list[str]:
        assert self.world is not None, "Database must be filled before querying"

        context = []
        context += list(map(lambda x: x.rule(), self.world.interactions.values()))
        context += list(map(lambda id, x: f"There is a '{x.type}' named '{id}'.", self.world.objects.keys(), self.world.objects.values()))
        #context += list(map(lambda id: f"There is a character named '{id}'.", self.world.characters.keys()))
        return context
