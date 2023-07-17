import pygame

class Tileset(list):
    """A tileset is a list of tiles (pygame.Surface objects)"""

    def __init__(self, path, size, margin, spacing):
        self.size = size
        self.margin = margin
        self.spacing = spacing

        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()

        # Extract tiles from the tileset and store them to self (which is a list)
        for x in range(self.margin, self.rect.size[0], self.size[0] + self.spacing):
            for y in range(self.margin, self.rect.size[1], self.size[1] + self.spacing):
                tile = pygame.Surface(self.size)
                tile.blit(self.image, (0, 0), (x, y, *self.size))
                self.append(tile)
