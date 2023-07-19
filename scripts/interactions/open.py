from world import Interaction

class Open(Interaction):
    def __init__(self, type_id: str, key_id: str):
        super().__init__(True)
        self.type_id = type_id
        self.key_id = key_id

    def rule(self) -> str:
        return f"Objects of type '{self.type_id}' can be opened with a '{self.key_id}'"

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        if target_id not in world.objects or world.objects[target_id].type != self.type_id:
            return f"Cannot open '{target_id}' because it is not of type '{self.type_id}'"
        if item_id != self.key_id:
            return f"'{target_id} can only be opened with a '{self.key_id}'"
        if self.key_id not in world.characters[chr_id].inventory:
            return f"Cannot open '{target_id}' because you do not have a '{self.key_id}'"

        world.objects.pop(target_id)
        return ""
