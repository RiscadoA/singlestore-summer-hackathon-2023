import pygame
import json

class Animation(list):
    """An animation is a list of frames to be displayed in sequence."""

    def __init__(self, source, size, start, step, count):
        for i in range(count):
            frame = pygame.Surface(size, pygame.SRCALPHA)
            frame.blit(source, (0, 0), (start[0] + i * step[0], start[1] + i * step[1], *size))
            self.append(frame)

    @staticmethod
    def load(image_path, json_path):
        """Load a dictionary of animations from a JSON file"""
        image = pygame.image.load(image_path).convert_alpha()

        with open(json_path) as file:
            data = json.load(file)
        for key in data:
            data[key] = Animation(source=image, **data[key])
        return data
