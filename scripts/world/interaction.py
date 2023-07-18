class Interaction:
    """Represents a possible interaction with an object"""

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        """Performs the interaction"""
        raise NotImplementedError()
