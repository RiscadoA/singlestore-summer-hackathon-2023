import openai
import json

from world import Action, Walk, Interact, Ask

class Prompt():
    """Interface for the prompt used by the AI"""

    async def fix(self, context: list[str], inventory: set[str], task: str, action: Action, error: str, exhausted: bool = False) -> list[str]:
        """Given the context, inventory, task, action and error message, returns a list of new tasks to replace the failed one"""
        raise NotImplementedError()

    async def execute(self, context: list[str], inventory: set[str], task: str) -> Action:
        """Given the context, inventory and task, returns the JSON string of the function to execute"""
        raise NotImplementedError()

class HumanPrompt(Prompt):
    """Implementation of the prompt which asks the user for input"""

    async def fix(self, context: list[str], inventory: set[str], task: str, action: Action, error: str, exhausted: bool) -> list[str]:
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

    async def execute(self, context: list[str], inventory: set[str], task: str) -> Action:
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

class OpenAIPrompt(Prompt):
    """Implementation of the prompt which uses the OpenAI API"""

    FUNCTIONS = [
        {
            "name": "walk",
            "description": "Walk to an object or character",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "The id of the object or character to walk to"
                    }
                },
                "required": ["target"]
            }
        },
        {
            "name": "interact",
            "description": "Interact with an object or character using something from your inventory",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "Id of the item on your inventory to use"
                    },
                    "target": {
                        "type": "string",
                        "description": "Id of the object or character to interact with"
                    }
                },
                "required": ["item", "target"]
            }
        }
    ]

    def __init__(self, api_key: str, model: str):
        openai.api_key = api_key
        self.model = model

    def sanitize(self, string: str) -> str:
        out = ""
        for line in string.split("\n"):
            out += line.replace("\t", " ").strip() + "\n"
        return out.strip()

    async def fix(self, context: list[str], inventory: set[str], task: str, action: Action, error: str, exhausted: bool) -> list[str]:
        if isinstance(action, Walk):
            action_str = f"walk({action.target})"
        elif isinstance(action, Interact):
            action_str = f"interact({action.item_id}, {action.target_id})"
        elif isinstance(action, Ask):
            action_str = f"ask({action.character_id}, {action.question})"
        else:
            assert False, f"Unsupported action type {type(action)}"

        if exhausted:
            goal = f"""
                Your goal is '{task}'. Decompose the goal into specific actions.
            """
        else:
            goal = f"""
                Your goal right now is '{task}', which you previously tried to achieve with the action '{action_str}' and
                failed with the error message '{error}'. Decompose the failed task into smaller tasks or correct it. 
            """

        newline = "\n"
        if exhausted:
            prompt = self.sanitize(f'''
                You are a character in a world. Decompose the goal '{task}' into one or more specific achievable actions, one per line, without any styling, formatting, numbering or headers.
                There are two possible questions: walking to a target, or interacting with a target using an item from your inventory.
                Use the information below to decide which actions to use:
                
                Information about the world:
                """
                {newline.join(context)}
                You have an inventory, which contains the following items: {", ".join(inventory)}.
                """
            ''')
        else:
            prompt = self.sanitize(f'''
                You are a character in a world. You tried to execute '{task}' but failed with the message '{error}'.
                Decompose the given goal into specific achievable actions, one per line, without any styling, formatting, numbering or headers.
                There are two possible questions: walking to a target, or interacting with a target using an item from your inventory.
                Use the information below to decide which actions to use:
                
                Information about the world:
                """
                {newline.join(context)}
                You have an inventory, which contains the following items: {", ".join(inventory)}.
                """
            ''')

        print()
        print("-------- OpenAI fix prompt --------")
        print(prompt)
        print()

        if exhausted:
            result = await openai.ChatCompletion.acreate(
                model=self.model,
                temperature=0.5,
                messages=[{"role": "system", "content": prompt}])
        else:
            result = await openai.ChatCompletion.acreate(
                model=self.model,
                temperature=0.5,
                messages=[{"role": "system", "content": prompt}])
        result = result["choices"][0]["message"]["content"] # type: ignore

        print()
        print("-------- OpenAI fix response --------")
        print(result)
        print()

        return result.split("\n")

    async def execute(self, context: list[str], inventory: set[str], task: str) -> Action:
        
        newline = "\n"
        prompt = self.sanitize(f'''
            You are a character in a world. Your goal is '{task}'. Instead of answering with text, you should call the
            functions walk and interact to achieve your goal.
            Use the information below to decide which function to call:
            
            Information about the world:
            """
            {newline.join(context)}
            You have an inventory, which contains the following items: {", ".join(inventory)}.
            """
        ''')

        print()
        print("-------- OpenAI execute prompt --------")
        print(prompt)
        print()

        result = await openai.ChatCompletion.acreate(
            model=self.model,
            temperature=0.0,
            messages=[{"role": "system", "content": prompt}],
            functions=self.FUNCTIONS)
        result = result["choices"][0]["message"] # type: ignore

        print()
        print("-------- OpenAI execute response --------")
        print(result)
        print()

        if "function_call" not in result:
            raise ValueError(f"OpenAI returned an invalid response without a function call: {result}")

        function_call = result["function_call"]
        arguments = json.loads(function_call["arguments"])
        if function_call["name"] == "walk":
            return Walk(arguments["target"])
        elif function_call["name"] == "interact":
            return Interact(arguments["item"], arguments["target"])
        else:
            raise ValueError(f"OpenAI returned an invalid function call: {function_call}")
