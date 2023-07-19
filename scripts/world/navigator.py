from typing import Union, Optional

from .object import Object
from .character import Character

def is_removeable(objects: dict[str, Object], occluded: str):
    if occluded not in objects:
        return False
    interaction = objects[occluded].interaction
    return interaction is None or interaction.removeable

class Node:
    def __init__(self):
        self.occluded = ""
        self.g_score = 0.0
        self.f_score = 0.0
        self.parent: Optional[tuple[int, int]] = None

class Navigator:
    def __init__(self, size: tuple[int, int], objects: dict[str, Object], characters: dict[str, Character]):
        self.size = size
        self.objects = objects
        self.characters = characters

        self.seen_objects = dict[str, tuple[int, int, int, int]]()
        self.nodes = [[Node() for _ in range(size[1])] for _ in range(size[0])]

    def occlude(self, what: str, area: tuple[int, int, int, int]):
        x, y, w, h = area
        for i in range(x, x + w):
            for j in range(y, y + h):
                assert self.nodes[i][j].occluded == ""
                self.nodes[i][j].occluded = what
    
    def unocclude(self, what: str, area: tuple[int, int, int, int]):
        x, y, w, h = area
        for i in range(x, x + w):
            for j in range(y, y + h):
                assert self.nodes[i][j].occluded == what
                self.nodes[i][j].occluded = ""

    def update_occlusion(self):
        removed = []
        for obj_id in self.seen_objects:
            if obj_id not in self.objects:
                x, y, w, h = self.seen_objects[obj_id]
                removed.append(obj_id)
                self.unocclude(obj_id, (x, y, w, h))
        for obj_id in removed:
            self.seen_objects.pop(obj_id)

        for obj_id, obj in self.objects.items():
            if obj_id not in self.seen_objects and obj.occlude:
                self.seen_objects[obj_id] = obj.position + obj.size
                self.occlude(obj_id, obj.position + obj.size)

    def heuristic(self, node: tuple[int, int], target: tuple[int, int]) -> int:
        return abs(node[0] - target[0]) + abs(node[1] - target[1])

    def get_path(self, origin: tuple[int, int], target: str) -> Union[str, list[tuple[int, int]]]:
        if target not in self.objects and target not in self.characters:
            return f"No such object or character '{target}'"
        self.update_occlusion()

        result = self.__get_path(origin, target, lambda node: node.occluded != "" and node.occluded != target)
        if result is not None:
            return result
        
        result = self.__get_path(origin, target, lambda node: node.occluded != "" and node.occluded != target and not is_removeable(self.objects, node.occluded))
        if result is not None:
            # Figure out which node is blocking the path
            for node in result:
                obj_id = self.nodes[node[0]][node[1]].occluded
                if obj_id != "" and obj_id != target:
                    return f"Cannot reach '{target}' because '{obj_id}' is blocking the path"
            return result

        return f"'{target}' is unreacheable"

    def __get_path(self, origin: tuple[int, int], target: str, occluded_filter) -> Optional[list[tuple[int, int]]]:
        if target not in self.objects:
            target_pos = self.characters[target].position
        else:
            target_pos = self.objects[target].position

        open_set = [origin]
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.nodes[x][y].g_score = float("inf")
                self.nodes[x][y].f_score = float("inf")
                self.nodes[x][y].parent = None

        self.nodes[origin[0]][origin[1]].g_score = 0.0
        self.nodes[origin[0]][origin[1]].f_score = self.heuristic(origin, target_pos)

        while open_set:
            current = min(open_set, key=lambda node: self.nodes[node[0]][node[1]].f_score)
            if current == target_pos:
                path = []
                while current:
                    if not occluded_filter(self.nodes[current[0]][current[1]]) and self.nodes[current[0]][current[1]].occluded != target and current != target_pos:
                        path.append(current)
                    current = self.nodes[current[0]][current[1]].parent
                return path[::-1]

            open_set.remove(current)
            for x, y in [(current[0] + 1, current[1]), (current[0] - 1, current[1]), (current[0], current[1] + 1), (current[0], current[1] - 1)]:
                if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
                    continue
                if occluded_filter(self.nodes[x][y]):
                    continue
                tentative_g_score = self.nodes[current[0]][current[1]].g_score + 1
                if tentative_g_score < self.nodes[x][y].g_score:
                    self.nodes[x][y].parent = current
                    self.nodes[x][y].g_score = tentative_g_score
                    self.nodes[x][y].f_score = tentative_g_score + self.heuristic((x, y), target_pos)
                    if (x, y) not in open_set:
                        open_set.append((x, y))

        return None
