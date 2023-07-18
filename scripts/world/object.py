from typing import Optional

from . import Interaction

class ObjectType:
    """Represents a type of object in the world"""

    def __init__(self, size: tuple[int, int], interaction: Optional[Interaction] = None):
        self.size = size
        self.interaction = interaction

class Object:
    """Represents a static object in the world, which may optionally be interacted with"""

    def __init__(self, type_id: str, position: tuple[int, int], type: ObjectType):
        self.type = type_id
        self.position = position
        self.size = type.size
        self.interaction = type.interaction
