from .direction import Direction

class Action:
    """An action that a character can perform"""

    def prepare(self, world, character_id: str):
        """Called when the action is first assigned to a character"""
        self.world = world
        self.character_id = character_id
        self.character = world.characters[character_id]
        self.error = ""

    def tick(self, delta_t: float) -> bool:
        """Updates the action, returning whether it is complete. Error should be set on failure"""
        raise NotImplementedError
    
class Idle(Action):
    """An action that does nothing"""

    def __init__(self, finish: bool = False):
        """If finish is False, the action will never complete"""
        self.finish = finish

    def tick(self, delta_t: float) -> bool:
        return self.finish

class Walk(Action):
    """An action that moves the character along a given path"""

    SPEED = 10

    def __init__(self, target: str):
        self.target = target

    def prepare(self, world, character_id: str):
        super().prepare(world, character_id)

        result = world.navigator.get_path(self.character.position, self.target)
        if isinstance(result, str):
            self.error = result
            self.path = []
        else:
            self.path = result

    def tick(self, delta_t: float) -> bool:
        # Calculate the distance the character can move in this frame
        moveable_dist = self.SPEED * delta_t
        if moveable_dist == 0:
            return False

        # While there is still distance to move, and there is a path to follow
        while moveable_dist > 0 and self.path:
            # Direction and distance from the character to the next position in the path
            target_dir = tuple(x - y for x, y in zip(self.path[0], self.character.animated_position))
            target_dist = (target_dir[0] ** 2 + target_dir[1] ** 2) ** 0.5

            if target_dist <= moveable_dist:
                # If the character can reach the next position in the path in this frame, move it there
                moveable_dist -= target_dist
                self.character.position = self.path[0]
                self.character.animated_position = self.path[0]
                self.path.pop(0)
            else:
                # Otherwise move the character as far as it can go in this frame
                self.character.animated_position = tuple(x + y / target_dist * moveable_dist for x, y in zip(self.character.animated_position, target_dir))
                moveable_dist = 0

            # Update the character's direction
            if target_dist > 0:
                self.character.animated_direction = Direction.from_vec(target_dir)

        return not self.path

class Interact(Action):
    """An action that makes the character interact with an object"""

    def __init__(self, item_id: str, target_id: str):
        self.item_id = item_id
        self.target_id = target_id
        self.interaction = None

    def prepare(self, world, character_id: str):
        super().prepare(world, character_id)

        if self.item_id not in self.character.inventory:
            self.error = f"Cannot interact with '{self.target_id}' because you do not have '{self.item_id}'"
            return
        
        if self.target_id not in self.world.objects:
            self.error = f"Cannot interact with '{self.target_id}' because it does not exist"
            return

        self.target = self.world.objects[self.target_id]
        dx = self.target.position[0] - self.character.position[0]
        dy = self.target.position[1] - self.character.position[1]
        if dx ** 2 + dy ** 2 > 1:
            self.error = f"Cannot interact with '{self.target_id}' because it is too far away"
            return
        
        if self.target.interaction is None:
            self.error = f"Cannot interact with '{self.target_id}' because it is not interactable"
            return

        self.interaction = self.target.interaction

    def tick(self, delta_t: float) -> bool:
        if self.interaction is not None:
            self.error = self.interaction.interact(self.world, self.character_id, self.item_id, self.target_id)
        return True

class Ask(Action):
    """An action that makes the character ask another character a question"""

    def __init__(self, target_id: str, question: str):
        self.target_id = target_id
        self.question = question
        self.answer = ""

    def prepare(self, world, character_id: str):
        super().prepare(world, character_id)

        self.target = None
        if self.target_id not in world.characters:
            self.error = f"Cannot ask '{self.target_id}' a question because they do not exist"
            return

        self.target = world.characters[self.target_id]
        self.target.action = Answer(self.target.action)
        self.target.action.prepare(world, self.target_id)

        self.walk = Walk(self.target_id)
        self.walk.prepare(world, character_id)

    def tick(self, delta_t: float) -> bool:
        if self.target is None:
            return True        

        if self.target.action.answer:
            # We got an answer, restore the target's previous action
            self.answer = self.target.action.answer
            self.target.action = self.target.action.previous
            return True
        elif not self.target.action.question:
            # We still need to ask the question, walk to the target
            if self.walk.tick(delta_t):
                if self.error:
                    return True
                self.target.action.question = self.question
            return False
        else:
            # We have asked the question, wait for an answer
            return False

class Answer(Action):
    """Action set automatically by a character to answer a question"""
    def __init__(self, previous: Action):
        self.previous = previous
        self.question = ""
        self.answer = ""

    def tick(self, delta_t: float) -> bool:
        # This action never completes by itself - Ask switches back to the previous action when it is done
        if self.question:
            self.answer = self.character.controller.answer(self.question)
        return False
