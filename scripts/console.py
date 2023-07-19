from typing import Optional

class Console:
    """A console that can be used to interact with the game"""

    def __init__(self):
        self.clear()

    def waiting(self) -> bool:
        """Returns True if the console is waiting for input, or False otherwise"""
        return self.printed and not self.submitted

    def print(self, text, end="\n"):
        """Prints text to the console, showing it to the user"""
        assert not self.printed, "Can only print before accepting input"
        self.display += text + end

    def accept(self) -> Optional[str]:
        """Returns the user input if it is available, or None otherwise"""
        if not self.submitted:
            self.printed = True
            return None

        value = self.input
        self.display = ""
        self.input = ""
        self.submitted = False
        return value

    def feed(self, text):
        """Feeds text to the console, as if the user had typed it"""
        if self.printed:
            self.input += text
            self.display += text

    def submit(self):
        """Submits the current input to the console, clearing it"""
        if self.printed:
            self.printed = False
            self.submitted = True

    def pop(self):
        """Removes the last character from the current input"""
        if not self.submitted and self.input:
            self.input = self.input[:-1]
            self.display = self.display[:-1]

    def clear(self):
        """Clears the console"""
        self.display = ""
        self.input = ""
        self.printed = False
        self.submitted = False
