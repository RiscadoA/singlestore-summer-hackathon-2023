from world import Interaction

class Win(Interaction):
    def __init__(self, item_id: str, goal_id: str, flag: list[bool]):
        super().__init__(False)
        self.item_id = item_id
        self.goal_id = goal_id
        self.flag = flag

    def rule(self) -> str:
        return f"You can win by interacting with '{self.goal_id}' using '{self.item_id}'."

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        if target_id not in world.objects or world.objects[target_id].type != self.goal_id:
            return f"Cannot win by interacting with '{target_id}' because it is not of type '{self.goal_id}'"
        if item_id != self.item_id:
            return f"You cannot win by interacting with '{target_id}' using '{item_id}'"
        self.flag[0] = True
        return ""
