import pygame

from world import World, Character, Idle, Walk, Ask, Answer, Object
from console import Console

from .tiles import TileLocator, Layers
from .animation import AnimationSet, AnimationPlayer
from .font import Font

TILES_PATH = "assets/tiles/overworld.json"
WALK_PATH = "assets/characters/walk.json"
FONT_PATH = "assets/font/simple.json"
CHARACTER_PATHS = {
    "blank": "assets/characters/blank.png",
    "guy": "assets/characters/guy.png",
    "red": "assets/characters/red.png",
    "green": "assets/characters/green.png",
    "blue": "assets/characters/blue.png",
}
OBJECTS_PATH = "assets/tiles/objects.png"
BUBBLES_PATH = "assets/tiles/bubbles.json"

class RendererCharacter:
    """Responsible for rendering a character"""

    def __init__(self, tile_size: tuple[int, int], character: Character, walk: AnimationSet, bubbles: AnimationSet):
        self.tile_size = tile_size
        self.character = character
        self.walk = walk
        self.bubbles = bubbles

        self.position = character.animated_position
        self.player = AnimationPlayer()
        self.bubble = AnimationPlayer()
        self.bubble_timer = 0.0
    
    def show_bubble(self, bubble: str, time: float):
        if self.bubble.animation == self.bubbles[bubble]:
            self.bubble_timer = time
        elif self.bubble_timer <= 0:
            self.bubble.play(self.bubbles[bubble])
            self.bubble_timer = time

    def tick(self, delta_t: float):
        is_ask_walk = False
        if isinstance(self.character.action, Ask) and not self.character.action.error:
            assert self.character.action.target is not None
            if isinstance(self.character.action.target.action, Answer):
                is_ask_walk = not self.character.action.target.action.question
        if isinstance(self.character.action, Walk) or is_ask_walk:
            if self.player.animation != self.walk[self.character.animated_direction]:
                self.player.play(self.walk[self.character.animated_direction])
        else:
            if self.player.is_playing():
                self.player.stop()

        if isinstance(self.character.action, Ask):
            self.show_bubble("ask", 1.0)
        elif isinstance(self.character.action, Answer):
            self.show_bubble("answer", 1.0)
        elif isinstance(self.character.action, Idle):
            if self.character.action.finish:
                self.show_bubble("think", 0.2)
            elif self.character.action.win:
                self.show_bubble("win", 1.0)

        if self.bubble_timer > 0:
            self.bubble.update(4 * delta_t)
            self.bubble_timer -= delta_t
            if self.bubble_timer <= 0:
                self.bubble.stop()

        self.position = self.character.animated_position
        self.player.update(1.5 * Walk.SPEED * delta_t)

    def render(self, surface: pygame.Surface):
        position = (self.position[0] * self.tile_size[0], (self.position[1] - 0.5) * self.tile_size[1])
        if self.player.is_playing():
            surface.blit(self.player.get_image(), position)
        else:
            surface.blit(self.walk[self.character.animated_direction][0], position)
        
        if self.bubble.is_playing():
            bubble_position = (position[0] + 1, position[1] - self.tile_size[1] * 0.4)
            surface.blit(self.bubble.get_image(), bubble_position)

class Renderer:
    def __init__(self, world: World, console: Console):
        self.world = world
        self.console = console

        self.tile_locator = TileLocator.load(TILES_PATH)
        self.character_animations = {}
        for character_id, path in CHARACTER_PATHS.items():
            self.character_animations[character_id] = AnimationSet.load(pygame.image.load(path).convert_alpha(), WALK_PATH)            
        self.font = Font(FONT_PATH)
        self.bubbles = AnimationSet.load(pygame.image.load(OBJECTS_PATH).convert_alpha(), BUBBLES_PATH)

        air_x, air_y, _, _ = self.tile_locator["air"]
        self.layers = Layers(self.tile_locator.tileset, world.size, (air_x, air_y))
        self.characters = {}
        self.objects = dict[str, Object]()

    def tick(self, delta_t: float):
        """Updates the renderer"""

        # Update the state of the rendered characters
        for character_id in self.world.characters:
            if character_id not in self.characters:
                if character_id in self.character_animations:
                    walk = self.character_animations[character_id]
                else:
                    walk = self.character_animations["blank"]

                self.characters[character_id] = RendererCharacter(
                    self.tile_locator.tileset.tile_size,
                    self.world.characters[character_id],
                    walk,
                    self.bubbles)
            self.characters[character_id].tick(delta_t)

        # Update the object tilemap, if necessary
        removed = []
        for obj_id, obj in self.objects.items():
            if obj_id not in self.world.objects:
                self.layers.objects.replace(obj.position, obj.size, self.layers.air)
        for obj_id in removed:
            self.objects.pop(obj_id)

        for obj_id, obj in self.world.objects.items():
            if obj_id not in self.objects:
                self.objects[obj_id] = obj
                self.layers.objects.place(obj.position, self.tile_locator[obj.type])
                

    def render(self, surface: pygame.Surface):
        """Renders the world to the given surface"""
        surface.blit(self.layers.ground.get_image(), (0, 0))
        surface.blit(self.layers.objects.get_image(), (0, 0))

        for character in sorted(self.characters.values(), key=lambda c: c.position[1]):
            character.render(surface)

        if self.console.display:
            self.font.render(surface, (256, 450), self.console.display)
