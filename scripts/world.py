import pygame
import numpy as np
from tiles import Tileset, Tilemap
from animation import Animation
from character import Character
from text import Font

OVERWORLD_TILES_PATH = "assets/tiles/overworld.png"
CHARACTER_PATH = "assets/character.png"
WALK_ANIMATION_PATH = "assets/animations/walk.json"
FONT_PATH = "assets/font/data.json"

class World:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((512, 512))

        tileset = Tileset(OVERWORLD_TILES_PATH, (16, 16), 0, 0)
        self.tilemap = Tilemap(tileset, (32, 32))
        self.tilemap.fill(0)
        self.tilemap.render()

        walk = Animation.load(CHARACTER_PATH, WALK_ANIMATION_PATH)
        self.character = Character(walk, (0, 0))
        for i in range(16):
            self.character.push_path((i * 16, (i + 1) * 16))
            self.character.push_path(((i + 1) * 16, (i + 1) * 16))

        self.font = Font(FONT_PATH)

    def run(self):
        running = True
        lastT = pygame.time.get_ticks()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            nowT = pygame.time.get_ticks()
            dT = (nowT - lastT) / 1000
            lastT = nowT

            self.character.update(dT)

            self.screen.blit(self.tilemap.image, (0, 0), self.tilemap.rect)
            self.character.render(self.screen)
            self.font.render(self.screen, (self.character.position[0], self.character.position[1] - 50), "Hey, whats up!\nHow are you doing? :D 123 Lines also break automatically wooooooo")
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    World().run()
