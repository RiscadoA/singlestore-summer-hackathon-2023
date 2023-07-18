import pygame

from world import World, HumanController
from renderer import Renderer
from console import Console
from interactions import Open
    
class App:
    def __init__(self):
        pygame.init()
        self.running = True

        self.console = Console()
        self.init_world()
        self.init_renderer()
        self.init_terrain()

    def __del__(self):
        pygame.quit()

    def init_world(self):
        self.world = World((32, 32))
        self.world.add_object_type("door", (1, 2), Open("door", "key"))
        self.world.add_object_type("goal", (2, 3))

        self.world.add_character("player", HumanController(self.console), (0, 0), {"key"})
        self.world.add_object("door", "door", (self.world.size[0] // 2, 5))
        self.world.add_object("goal", "goal", (20, 10))

    def init_terrain(self):
        for i in range(0, self.world.size[0] // 2 - 1):
            self.place_terrain("cliff-m", (i, 3))
        self.place_terrain("cliff-r", (self.world.size[0] // 2 - 1, 1))
        self.place_terrain("cliff-l", (self.world.size[0] // 2 + 1, 1))
        for i in range(self.world.size[0] // 2 + 2, self.world.size[0]):
            self.place_terrain("cliff-m", (i, 3))

    def place_terrain(self, area: str, position: tuple[int, int]):
        self.renderer.layers.ground.place(position, self.renderer.tile_locator[area])
        _, _, w, h = self.renderer.tile_locator[area]
        self.world.make_impassable(position + (w, h))

    def init_renderer(self):
        self.screen = pygame.display.set_mode((self.world.size[0] * 16, self.world.size[1] * 16))
        self.renderer = Renderer(self.world, self.console)

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
        self.screen.fill((0, 0, 0))
        self.renderer.render(self.screen)
        pygame.display.flip()

    def run(self):
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

if __name__ == "__main__":
    App().run()
