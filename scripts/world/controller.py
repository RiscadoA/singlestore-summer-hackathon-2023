from .action import Action, Idle, Walk, Interact

class Controller:
    def prepare(self, world, character_id: str):
        """Called when the controller is assigned to a character"""
        self.world = world
        self.character_id = character_id
        self.character = self.world.characters[character_id]

    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        return Walk("door")

class HumanController(Controller):
    def next_action(self, error: str = "") -> Action:
        """Called with the error message of the previous action if it failed, and returns the next action"""
        if error:
            print(error)
        else:
            print("Inventory: {}".format(", ".join(self.character.inventory)))
       
        while True:
            print("> ", end="")
            command = input().split(" ")
            if len(command) == 2 and command[0] == "walk":
                return Walk(command[1])
            elif len(command) == 3 and command[0] == "interact":
                return Interact(command[1], command[2])
            else:
                print("Invalid command, must be one of: walk <target>, interact <item> <target>")
