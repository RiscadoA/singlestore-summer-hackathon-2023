import pygame

from world import World, Character, Walk

from .tiles import TileLocator, Layers
from .animation import AnimationSet, AnimationPlayer

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
    def __init__(self, world: World):
        self.world = world

        self.tile_locator = TileLocator.load(TILES_PATH)
        self.character_animations = AnimationSet.load(pygame.image.load(GUY_PATH).convert_alpha(), WALK_PATH)

        self.layers = Layers(self.tile_locator.tileset, world.size)
        self.characters = {}

    def tick(self, delta_t: float):
        """Updates the renderer"""
        for character_id in self.world.characters:
            if character_id not in self.characters:
                self.characters[character_id] = RendererCharacter(
                    self.tile_locator.tileset.tile_size,
                    self.world.characters[character_id],
                    self.character_animations)
            self.characters[character_id].tick(delta_t)

    def render(self, surface: pygame.Surface):
        """Renders the world to the given surface"""
        surface.blit(self.layers.ground.get_image(), (0, 0))
        surface.blit(self.layers.objects.get_image(), (0, 0))

        for character in self.characters.values():
            character.render(surface)

