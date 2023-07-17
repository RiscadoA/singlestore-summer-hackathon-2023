import pygame
import numpy as np

class Tileset(list):
    """A tileset is a list of tiles (pygame.Surface objects)"""

    def __init__(self, path, size, margin, spacing):
        self.size = size
        self.margin = margin
        self.spacing = spacing

        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()

        # Extract tiles from the tileset and store them to self (which is a list)
        for y in range(self.margin, self.rect.size[1], self.size[1] + self.spacing):
            for x in range(self.margin, self.rect.size[0], self.size[0] + self.spacing):
                tile = pygame.Surface(self.size)
                tile.blit(self.image, (0, 0), (x, y, *self.size))
                self.append(tile)

class Tilemap:
    """A tilemap is a 2D array of tiles which render to an image"""

    def __init__(self, tileset: Tileset, size: tuple[int, int]):
        self.tileset = tileset

        self.size = size
        self.tiles = np.zeros(size, dtype=int)
        self.image = pygame.Surface((size[0] * tileset.size[0], size[1] * tileset.size[1]))
        self.rect = self.image.get_rect()

    def render(self):
        """Updates the image of the tilemap"""
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.image.blit(self.tileset[self[x, y]], (x * self.tileset.size[0], y * self.tileset.size[1]))

    def fill(self, tile: int):
        """Fills the entire tilemap with the specified tile"""
        self.tiles.fill(tile)

    def __setitem__(self, key: tuple[int, int], value: int):
        self.tiles[key] = value

    def __getitem__(self, key: tuple[int, int]):
        return self.tiles[key]
