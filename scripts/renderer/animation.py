import pygame
import json

class Animation(list[pygame.Surface]):
    """An animation is a list of frames to be displayed in sequence."""

class AnimationSet(dict[str, Animation]):
    """An animation set is a dictionary of animations"""

    @staticmethod
    def load(image: pygame.Surface, path: str) -> "AnimationSet":
        """Loads an animation set from a JSON file"""
        with open(path) as file:
            data = json.load(file)

        animations = {}
        for name, frames in data.items():
            animations[name] = Animation([image.subsurface(frame) for frame in frames])
        return AnimationSet(animations)

class AnimationPlayer:
    """Allows playing animations, storing the current frame and time"""

    def __init__(self):
        """Creates an animation player"""
        self.animation = None

    def play(self, animation: Animation):
        """Plays an animation"""
        self.animation = animation
        self.frame = 0.0

    def stop(self):
        """Stops playing any animation"""
        self.animation = None

    def is_playing(self) -> bool:
        """Returns whether an animation is playing"""
        return self.animation is not None

    def update(self, delta_t: float):
        """Updates the animation player"""
        if self.animation is not None:
            self.frame += delta_t
            if self.frame >= len(self.animation):
                self.frame = 0.0

    def get_image(self) -> pygame.Surface:
        """Returns the current frame of the animation"""
        assert self.animation is not None, "No animation is playing"
        return self.animation[int(self.frame)]
