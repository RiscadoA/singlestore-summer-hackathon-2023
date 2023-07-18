from typing import Optional

from . import Interaction

class Object:
    """Represents a static object in the world, which may optionally be interacted with"""

    def __init__(self, type: str, position: tuple[int, int], interaction: Optional[Interaction] = None):
        self.type = type
        self.position = position
        self.interaction = interaction
