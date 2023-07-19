from world import Action, Walk, Interact, Ask

class Prompt():
    """Interface for the prompt used by the AI"""

    def fix(self, context: list[str], inventory: set[str], task: str, action: Action, error: str) -> list[str]:
        """Given the context, inventory, task, action and error message, returns a list of new tasks to replace the failed one"""
        raise NotImplementedError()

    def execute(self, context: list[str], inventory: set[str], task: str) -> Action:
        """Given the context, inventory and task, returns the JSON string of the function to execute"""
        raise NotImplementedError()

class HumanPrompt(Prompt):
    """Implementation of the prompt which asks the user for input"""

    def fix(self, context: list[str], inventory: set[str], task: str, action: Action, error: str) -> list[str]:
        print(f"Context: {context}")
        print(f"Inventory: {inventory}")
        print(f"Task: {task}")
        print(f"Action: {action}")
        print(f"Error: {error}")
        print(f"Enter new tasks, one per line. Enter an empty line to finish.")
        new_tasks = []
        while True:
            new_task = input()
            if not new_task:
                break
            new_tasks.append(new_task)
        return new_tasks

    def execute(self, context: list[str], inventory: set[str], task: str) -> Action:
        print(f"Context: {context}")
        print(f"Inventory: {inventory}")
        print(f"Task: {task}")
        print(f"Enter action:")
        while True:
            action = input().split(" ")
            if len(action) == 2 and action[0] == "walk":
                return Walk(action[1])
            elif len(action) == 3 and action[0] == "interact":
                return Interact(action[1], action[2])
            elif len(action) >= 2 and action[0] == "ask":
                return Ask(action[1], " ".join(action[2:]))
            else:
                print("Invalid action")
