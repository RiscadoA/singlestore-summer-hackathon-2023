import pygame

from world import World, Character, Walk
from console import Console

from .tiles import TileLocator, Layers
from .animation import AnimationSet, AnimationPlayer
from .font import Font

TILES_PATH = "assets/tiles/overworld.json"
WALK_PATH = "assets/characters/walk.json"
GUY_PATH = "assets/characters/guy.png"
FONT_PATH = "assets/font/simple.json"

class RendererCharacter:
    """Responsible for rendering a character"""

    def __init__(self, tile_size: tuple[int, int], character: Character, animations: AnimationSet):
        self.tile_size = tile_size
        self.character = character
        self.animations = animations
        self.position = character.animated_position

        self.player = AnimationPlayer()

    def tick(self, delta_t: float):
        if isinstance(self.character.action, Walk):
            if self.player.animation != self.animations[self.character.animated_direction]:
                self.player.play(self.animations[self.character.animated_direction])
        elif self.player.is_playing():
            self.player.stop()

        self.position = self.character.animated_position
        self.player.update(1.5 * Walk.SPEED * delta_t)

    def render(self, surface: pygame.Surface):
        position = tuple(int(x * self.tile_size[i]) for i, x in enumerate(self.position))
        if self.player.is_playing():
            surface.blit(self.player.get_image(), position)
        else:
            surface.blit(self.animations[self.character.animated_direction][0], position)

class Renderer:
    def __init__(self, world: World, console: Console):
        self.world = world
        self.console = console

        self.tile_locator = TileLocator.load(TILES_PATH)
        self.character_animations = AnimationSet.load(pygame.image.load(GUY_PATH).convert_alpha(), WALK_PATH)
        self.font = Font(FONT_PATH)

        self.layers = Layers(self.tile_locator.tileset, world.size)
        self.characters = {}
        self.objects = set()

    def tick(self, delta_t: float):
        """Updates the renderer"""

        # Update the state of the rendered characters
        for character_id in self.world.characters:
            if character_id not in self.characters:
                self.characters[character_id] = RendererCharacter(
                    self.tile_locator.tileset.tile_size,
                    self.world.characters[character_id],
                    self.character_animations)
            self.characters[character_id].tick(delta_t)

        # Update the object tilemap, if necessary
        for obj_id, obj in self.world.objects.items():
            if obj_id not in self.objects:
                self.objects.add(obj_id)
                self.layers.objects.place(obj.position, self.tile_locator[obj.type])

    def render(self, surface: pygame.Surface):
        """Renders the world to the given surface"""
        surface.blit(self.layers.ground.get_image(), (0, 0))
        surface.blit(self.layers.objects.get_image(), (0, 0))

        for character in self.characters.values():
            character.render(surface)

        if self.console.display:
            self.font.render(surface, (256, 450), self.console.display)