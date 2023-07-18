class Interaction:
    """Represents a possible interaction with an object"""

    def __init__(self, removeable: bool) -> None:
        self.removeable = removeable

    def rule(self) -> str:
        """Returns a string describing the interaction"""
        raise NotImplementedError()

    def interact(self, world, chr_id: str, item_id: str, target_id: str) -> str:
        """Performs the interaction"""
        raise NotImplementedError()
