from world import Interaction

class Open(Interaction):
    def __init__(self, type_id: str, key_id: str):
        self.type_id = type_id
        self.key_id = key_id
        self.open = False

    def rule(self) -> str:
        return f"Objects of type '{self.type_id}' can be opened with a '{self.key_id}'"

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        if self.open:
            return f"'{target_id}' is already open"
        if item_id != self.key_id:
            return f"'{target_id} can only be opened with a '{self.key_id}'"
        if self.key_id not in world.characters[chr_id].inventory:
            return f"Cannot open '{target_id}' because you do not have a '{self.key_id}'"

        world.objects.pop(target_id)
        self.open = True
        return ""
