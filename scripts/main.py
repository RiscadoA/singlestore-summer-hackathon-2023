import pygame

from world import World, Interaction, Controller
from renderer import Renderer

class Open(Interaction):
    def __init__(self, key_id: str):
        self.key_id = key_id
        self.open = False

    def interact(self, world: World, chr_id: str, item_id: str, target_id: str) -> str:
        if self.open:
            return f"'{target_id}' is already open"
        if item_id != self.key_id:
            return f"'{target_id} can only be opened with a '{self.key_id}'"
        if not world.characters[chr_id].inventory:
            return f"Cannot open '{target_id}' because you do not have a '{self.key_id}'"
        
        self.open = True
        return ""
    
class App:
    def __init__(self):
        pygame.init()
        self.running = True

        self.init_world()
        self.init_renderer()

    def __del__(self):
        pygame.quit()

    def init_world(self):
        self.world = World((32, 32))
        self.world.add_character("player", Controller(), (0, 0), {"key"})
        self.world.add_object("door", (31, 31), Open("key"))

    def init_renderer(self):
        self.screen = pygame.display.set_mode((self.world.size[0] * 16, self.world.size[1] * 16))
        self.renderer = Renderer(self.world)

    def poll_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

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
