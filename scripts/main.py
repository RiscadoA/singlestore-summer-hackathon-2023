import pygame

from world import World, Interaction, HumanController
from renderer import Renderer
from console import Console

class Open(Interaction):
    def __init__(self, type_id: str, key_id: str):
        self.type_id = type_id
        self.key_id = key_id
        self.open = False

    def rule(self) -> str:
        return f"Objects of type '{self.type_id}' can be opened with a '{self.key_id}'"

    def interact(self, world: World, chr_id: str, item_id: str, target_id: str) -> str:
        if self.open:
            return f"'{target_id}' is already open"
        if item_id != self.key_id:
            return f"'{target_id} can only be opened with a '{self.key_id}'"
        if self.key_id not in world.characters[chr_id].inventory:
            return f"Cannot open '{target_id}' because you do not have a '{self.key_id}'"

        self.open = True
        return ""
    
class App:
    def __init__(self):
        pygame.init()
        self.running = True

        self.console = Console()
        self.init_world()
        self.init_renderer()

    def __del__(self):
        pygame.quit()

    def init_world(self):
        self.world = World((32, 32))
        self.world.add_object_type("door", (1, 2), Open("door", "key"))
        self.world.add_object_type("goal", (2, 3))

        self.world.add_character("player", HumanController(self.console), (0, 0), {"key"})
        self.world.add_object("door", "door", (10, 10))
        self.world.add_object("door", "door2", (3, 0))
        self.world.add_object("goal", "goal", (20, 10))

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
