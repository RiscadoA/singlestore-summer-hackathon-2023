import pygame

class Animation(list):
    """An animation is a list of frames to be displayed in sequence."""

    def __init__(self, path, size, start, step, count):
        self.image = pygame.image.load(path)
        rect = self.image.get_rect()

        for i in range(count):
            frame = pygame.Surface(size)
            frame.blit(self.image, (0, 0), (start[0] + i * step[0], start[1] + i * step[1], *size))
            self.append(frame)
