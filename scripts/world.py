import pygame
import numpy as np
from tiles import Tileset, Tilemap

OVERWORLD_TILES_PATH = "assets/tiles/overworld.png"

class World:
    def __init__(self):
        pygame.init()

        tileset = Tileset(OVERWORLD_TILES_PATH, (16, 16), 0, 0)
        self.tilemap = Tilemap(tileset, (32, 32))
        self.tilemap.fill(0)
        self.tilemap.render()

        self.screen = pygame.display.set_mode((self.tilemap.rect.width, self.tilemap.rect.height))
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.tilemap.image, (0, 0), self.tilemap.rect)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

if __name__ == "__main__":
    World().run()