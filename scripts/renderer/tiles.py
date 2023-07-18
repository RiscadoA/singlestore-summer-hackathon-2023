import pygame
import json

class Tileset:
    """Stores a set of tiles"""

    def __init__(self, tiles: list[list[pygame.Surface]]):
        """Creates a tileset from a 2D array of tiles"""
        self.tiles = tiles
        self.tile_size = tiles[0][0].get_size()
        for row in tiles:
            for tile in row:
                assert tile.get_size() == self.tile_size, "All tiles in a set must be of the same size"

    def __getitem__(self, key: tuple[int, int]) -> pygame.Surface:
        x, y = key
        return self.tiles[x][y]

    @staticmethod
    def load(path: str, size: tuple[int, int]) -> "Tileset":
        """Loads a tileset from an image at a given path"""
        image = pygame.image.load(path).convert_alpha()
        w, h = image.get_size()

        tiles = []
        for x in range(0, w, size[0]):
            column = []
            for y in range(0, h, size[1]):
                column.append(image.subsurface((x, y, *size)))
            tiles.append(column)
        return Tileset(tiles)

class Tilemap:
    """A tilemap is a 2D array of tiles which render to an image"""

    def __init__(self, tileset: Tileset, size: tuple[int, int], default: tuple[int, int] = (0, 0)):
        """Creates a tilemap with the given tileset, size and default tile"""
        self.tileset = tileset
        self.size = size

        self.tiles = [[default for _ in range(size[1])] for _ in range(size[0])]
        self.image = pygame.Surface((size[0] * tileset.tile_size[0], size[1] * tileset.tile_size[1]), pygame.SRCALPHA)
        self.dirty = True

    def get_image(self):
        """Returns an image of the tilemap"""
        if self.dirty:
            self.dirty = False
            for x in range(self.size[0]):
                for y in range(self.size[1]):
                    tile = self.tileset[self.tiles[x][y]]
                    self.image.blit(tile, (x * self.tileset.tile_size[0], y * self.tileset.tile_size[1]))
        return self.image

    def fill(self, tile: tuple[int, int]):
        """Fills the entire tilemap with the specified tile"""
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self[x, y] = tile

    def place(self, position, area: tuple[int, int, int, int]):
        """Pastes the given area from the tileset into the tilemap"""
        t, u, w, h = area
        for x in range(w):
            for y in range(h):
                self[position[0] + x, position[1] + y] = (t + x, u + y)

    def __setitem__(self, key: tuple[int, int], value: tuple[int, int]):
        self.dirty = True
        x, y = key
        self.tiles[x][y] = value

    def __getitem__(self, key: tuple[int, int]) -> tuple[int, int]:
        x, y = key
        return self.tiles[x][y]

class TileLocator:
    """Stores the location of tile areas in a tileset"""

    def __init__(self, tileset: Tileset, areas: dict[str, tuple[int, int, int, int]] = {}):
        """Creates a locator for the given tileset with the given areas"""
        self.tileset = tileset
        self.areas = areas

    def __setitem__(self, key: str, value: tuple[int, int, int, int]):
        self.areas[key] = value

    def __getitem__(self, key: str) -> tuple[int, int, int, int]:
        return self.areas[key]

    @staticmethod
    def load(path: str) -> "TileLocator":
        """Loads a tile locator and its tileset from a file"""
        with open(path) as file:
            data = json.load(file)
        tileset = Tileset.load(data["image"], data["tile_size"])
        return TileLocator(tileset, data["areas"])

class Layers:
    """Stores the tilemap layers for a world"""

    def __init__(self, tileset: Tileset, size: tuple[int, int]):
        """Creates a set of layers with the given tileset and size, in tiles"""
        self.ground = Tilemap(tileset, size)
        self.objects = Tilemap(tileset, size)
