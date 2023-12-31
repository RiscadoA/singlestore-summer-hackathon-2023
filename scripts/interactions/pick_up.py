from world import Interaction

class PickUp(Interaction):
    def __init__(self, item_id: str, tool_id: str):
        super().__init__(True)
        self.item_id = item_id
        self.tool_id = tool_id

    def rule(self) -> str:
        return f"You can pick up a '{self.item_id}' with a '{self.tool_id}'."

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        if target_id not in world.objects or world.objects[target_id].type != self.item_id:
            return f"Cannot open '{target_id}' because it is not of type '{self.item_id}'"
        if item_id != self.tool_id:
            return f"'{target_id} can only be picked up with a '{self.tool_id}'"
        if self.tool_id not in world.characters[chr_id].inventory:
            return f"Cannot pick up '{target_id}' because you do not have a '{self.tool_id}'"
        if target_id in world.characters[chr_id].inventory:
            return f"Cannot pick up '{target_id}' because you already have it"

        world.objects.pop(target_id)
        world.characters[chr_id].inventory.add(target_id)
        return ""
