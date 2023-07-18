class Direction:
    NORTH = "north"
    WEST = "west"
    SOUTH = "south"
    EAST = "east"

    @staticmethod
    def from_vec(vec: tuple[float, float]) -> str:
        """Converts a direction vector to a string representing a direction"""
        if vec[0] > 0:
            return Direction.EAST
        elif vec[0] < 0:
            return Direction.WEST
        elif vec[1] > 0:
            return Direction.SOUTH
        elif vec[1] < 0:
            return Direction.NORTH
        else:
            assert False, "Direction vector cannot be (0, 0)"
