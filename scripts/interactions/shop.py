from world import Interaction

class Shop(Interaction):
    def __init__(self, where_id: str, buy_item: str, sell_item: str):
        super().__init__(True)
        self.where_id = where_id
        self.buy_item = buy_item
        self.sell_item = sell_item

    def rule(self) -> str:
        return f"By interacting with a '{self.buy_item}' and a '{self.where_id}', you can get a '{self.sell_item}'"

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        assert self.where_id == target_id

        if item_id != self.buy_item:
            return f"'{self.where_id}' does not buy '{item_id}', it buys '{self.buy_item}'"
        if item_id not in world.characters[chr_id].inventory:
            return f"Cannot sell '{item_id}' because you do not have it"
        if self.sell_item in world.characters[chr_id].inventory:
            return f"Cannot buy '{self.sell_item}' because you already have it"
        
        world.characters[chr_id].inventory.remove(item_id)
        world.characters[chr_id].inventory.add(self.sell_item)
        return ""
