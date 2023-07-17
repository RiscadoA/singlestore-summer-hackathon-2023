import pygame
import numpy as np
from animation import Animation

class Character:
    WALK_SPEED = 64
    WALK_ANIMATION_SPEED = WALK_SPEED * 0.1

    def __init__(self, walk_animations, position):
        self.walk_animations = walk_animations
        self.position = np.array(position, dtype=float)

        self.path = []
        self.frame = 0
        self.direction = "south"
    
    def push_path(self, position):
        self.path.append(np.array(position, dtype=float))

    def update(self, dT):
        if self.path:
            # Calculate the distance the character can move in this frame
            walk_dist = self.WALK_SPEED * dT
            if walk_dist == 0:
                return

            # Move the character towards the next position in the path until it reaches it
            walk_dir = self.path[0] - self.position
            current_dist = np.linalg.norm(walk_dir)
            if current_dist < walk_dist:
                self.position = self.path[0]
                self.path.pop(0)
                self.frame = 0
            else:
                self.position += walk_dir / current_dist * walk_dist

                # Figure out in which direction the character is walking
                if walk_dir[0] > 0:
                    self.direction = "east"
                elif walk_dir[0] < 0:
                    self.direction = "west"
                elif walk_dir[1] > 0:
                    self.direction = "south"
                elif walk_dir[1] < 0:
                    self.direction = "north"

                # Play the walking animation
                self.frame += self.WALK_ANIMATION_SPEED * dT
                if self.frame >= len(self.walk_animations[self.direction]):
                    self.frame = 0

    def render(self, surface):
        image = self.walk_animations[self.direction][int(self.frame)]
        surface.blit(image, self.position)
