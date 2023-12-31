import pygame
import logging
import asyncio

from typing import Optional

from world import World, Controller, Interaction
from renderer import Renderer
from console import Console

SCALE = 2

class App:
    def __init__(self, size: tuple[int, int]):
        self.size = size

        pygame.init()
        logging.basicConfig(level=logging.INFO)

        self.console = Console()
        self.world = World(size)
        self.screen = pygame.display.set_mode((self.world.size[0] * 16 * SCALE, self.world.size[1] * 16 * SCALE))
        self.orig_screen = pygame.Surface((self.world.size[0] * 16, self.world.size[1] * 16))
        self.renderer = Renderer(self.world, self.console)
        self.running = True

    def __del__(self):
        pygame.quit()

    def add_interaction(self, type: str, interaction: Interaction):
        self.world.add_interaction(type, interaction)

    def add_object_type(self, name: str, interaction: Optional[Interaction] = None, occlude=True):
        _, _, w, h = self.renderer.tile_locator[name]
        self.world.add_object_type(name, (w, h), interaction, occlude)
    
    def add_object(self, type_id: str, name: str, position: tuple[int, int]):
        if type_id not in self.world.object_types:
            self.add_object_type(type_id)
        self.world.add_object(type_id, name, position)

    def add_character(self, name: str, controller: Controller, position: tuple[int, int], inventory: set[str] = set()):
        self.world.add_character(name, controller, position, inventory)

    def place_ground(self, area: str, position: tuple[int, int], impassable: bool = True):
        self.renderer.layers.ground.place(position, self.renderer.tile_locator[area])
        if impassable:
            _, _, w, h = self.renderer.tile_locator[area]
            self.world.make_impassable(position + (w, h))

    def place_decor(self, area: str, position: tuple[int, int], impassable: bool = True):
        self.renderer.layers.objects.place(position, self.renderer.tile_locator[area])
        if impassable:
            _, _, w, h = self.renderer.tile_locator[area]
            self.world.make_impassable(position + (w, h))

    def poll_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.console.submit()
                elif event.key == pygame.K_BACKSPACE:
                    self.console.pop()
                elif event.unicode:
                    self.console.feed(event.unicode)

    def tick(self, delta_t: float):
        self.world.tick(delta_t)
        self.renderer.tick(delta_t)
    
    def render(self):
        self.orig_screen.fill((0, 0, 0))
        self.renderer.render(self.orig_screen)
        pygame.transform.scale(self.orig_screen, self.screen.get_size(), self.screen)
        pygame.display.flip()

    async def async_run(self):
        last_t = pygame.time.get_ticks()
        while True:
            self.poll_events()
            if not self.running:
                break

            now_t = pygame.time.get_ticks()
            delta_t = (now_t - last_t) / 1000
            last_t = now_t

            self.tick(delta_t)
            self.render()
            await asyncio.sleep(0.01)

    def run(self):
        asyncio.run(self.async_run())
