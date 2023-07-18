from typing import Union

from .object import Object

class Navigator:
    def __init__(self, size: tuple[int, int], objects: dict[str, Object]):
        self.size = size
        self.objects = objects

    def get_path(self, origin: tuple[int, int], target: str) -> Union[str, list[tuple[int, int]]]:
        if target not in self.objects:
            return f"No such object '{target}'"
        # TODO: implement actual pathfinding
        return [self.objects[target].position]
