import pygame
import json

class Font:
    """Used to draw text from bitmap fonts"""

    def __init__(self, path: str):
        with open(path) as file:
            data = json.load(file)
        self.image = pygame.image.load(data["image"]).convert_alpha()
        self.characters = {}
        self.line_height = data["line_height"]
        self.background_margin = data["background_margin"]

        for character in data["characters"]:
            x, y, w, h = data["characters"][character]
            img = pygame.Surface((w, h), pygame.SRCALPHA)
            img.blit(self.image, (0, 0), (x, y, w, h))
            self.characters[character] = {
                "image": img,
                "size": (w, h),
            }
    
    def available_widelta_th(self):
        """Returns how many pixels fit on a line"""
        return self.characters["background"]["size"][0] - self.background_margin[0] * 2

    def text_widelta_th(self, text: str):
        """Returns how many pixels wide the text is"""
        widelta_th = 0
        for character in text:
            assert character != '\n', "Newlines are not supported here"
            widelta_th += self.characters[character]["size"][0]
        return widelta_th

    def render_raw(self, surface: pygame.Surface, position: tuple[int, int], text: str):
        """Renders text to a surface, without any centering or automatic line breaks"""
        surface.blit(self.characters["background"]["image"], position)
        x, y = position
        x += self.background_margin[0]
        y += self.background_margin[1]

        for character in text:
            if character == '\n':
                x = position[0] + self.background_margin[0]
                y += self.line_height
            else:
                surface.blit(self.characters[character]["image"], (x, y))
                x += self.characters[character]["size"][0]

    def render(self, surface: pygame.Surface, center: tuple[int, int], text: str):
        """Renders text to a surface"""
        processed = ""
        for line in text.split("\n"):
            processed_line = ""
            for word in line.split(" "):
                if processed_line:
                    if self.text_widelta_th(processed_line + " " + word) > self.available_widelta_th():
                        processed += processed_line + "\n"
                        processed_line = ""
                    else:
                        processed_line += " "
                processed_line += word
            processed += processed_line + "\n"

        _, _, w, h = self.characters["background"]["image"].get_rect() 
        position = (center[0] - w // 2, center[1] - h // 2)
        self.render_raw(surface, position, processed)
