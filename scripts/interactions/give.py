from world import Interaction

class Give(Interaction):
    def __init__(self, disallowed_items: set[str] = set()):
        super().__init__(True)
        self.disallowed_items = disallowed_items

    def rule(self) -> str:
        return f"Items can be given to other characters by interacting with them"

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        if target_id not in world.characters:
            return f"Cannot give '{item_id}' to '{target_id}' because they are not a character"
        if item_id not in world.characters[chr_id].inventory:
            return f"Cannot give '{item_id}' to '{target_id}' because you do not have it"
        if item_id in self.disallowed_items:
            return f"Giving '{item_id}' to '{target_id}' is not allowed"
        if item_id in world.characters[target_id].inventory:
            return f"{target_id} already has '{item_id}'"

        world.characters[target_id].inventory.add(item_id)
        return ""
