import openai
import json

from world import Action, Walk, Interact, Ask

class Prompt():
    """Interface for the prompt used by the AI"""

    async def plan(self, context: list[str], inventory: set[str], goal: str) -> list[str]:
        """Given the context, inventory and goal, returns a list of tasks to achieve the goal"""
        raise NotImplementedError()

    async def execute(self, context: list[str], inventory: set[str], plan: list[str]) -> tuple[object, Action]:
        """Given the context, inventory and task, returns the JSON string of the function to execute"""
        raise NotImplementedError()

    async def reevaluate(self, context: list[str], memory: object, plan: list[str], goal: str, error: str = "") -> list[str]:
        """Given the memory and error message, returns a list of new tasks"""
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
    
    async def plan(self, context: list[str], inventory: set[str], goal: str) -> list[str]:
        newline = "\n"
        prompt = self.sanitize(f'''
            You are a character in a world.
            Your final goal is '{goal}'.
            Taking into account the information below about the world, decompose the goal into a plan of one or more specific achievable tasks.
            Write a numbered list where each line corresponds to a single task.
            Each task should a single, concise sentence, and be achievable using the functions walk and interact.
            You have an inventory, which contains the following items: {", ".join(inventory)}.

            Example plan:
            1. Get Y
            2. Walk to X
            3. Interact with X using Y

            Information about the world (ranked from most to least important):
            """
            {newline.join(context)}
            """
        ''')

        result = await openai.ChatCompletion.acreate(
                model=self.model,
                temperature=0.5,
                messages=[{"role": "system", "content": prompt}],
                functions=self.FUNCTIONS)
        content = result["choices"][0]["message"]["content"] # type: ignore

        print()
        print(f"-------- OpenAI plan response --------")
        print(content)
        print()

        # TODO: validate plan
        return [task.strip() for task in content.split("\n")]

    async def execute(self, context: list[str], inventory: set[str], plan: list[str]) -> tuple[object, Action]:
        newline = "\n"
        prompt = self.sanitize(f'''
            You are a character in a world.
            Taking into account the information below about the world, call the function which gets you closer to completing the first task in the plan below.
            Perform the task by calling one of the functions walk and interact exposed to you by the API.
            You have an inventory, which contains the following items: {", ".join(inventory)}.

            Your current plan is:
            {newline.join(plan)}

            Information about the world (ranked from most to least important):
            """
            {newline.join(context)}
            """
        ''')

        memory = [{"role": "system", "content": prompt}]

        while True:
            result = await openai.ChatCompletion.acreate(
                    model=self.model,
                    temperature=0.5,
                    messages=memory,
                    functions=self.FUNCTIONS)
            message = result["choices"][0]["message"] # type: ignore
            memory += [message]

            if "function_call" in message:
                function_call = message["function_call"]
                if function_call["name"] in ["walk", "interact"]:
                    break

            memory += [{"role": "system", "content": "You must call either the walk or interact function"}]

        print()
        print(f"-------- OpenAI execute response --------")
        print(memory[-1]["function_call"])
        print()

        memory = [memory[0], memory[-1]]
        arguments = json.loads(function_call["arguments"])
        if function_call["name"] == "walk":
            return (memory, Walk(arguments["target"]))
        elif function_call["name"] == "interact":
            return (memory, Interact(arguments["item"], arguments["target"]))
        else:
            assert False, "bah!"

    async def reevaluate(self, context: list[str], memory: list, plan: list[str], goal: str, error: str = "") -> list[str]:
        newline = "\n"
        if error:
            what = "error"
            prompt = self.sanitize(f'''
                Function failed with error: {error}
                Your final goal is '{goal}'.
                Reevaluate your plan taking into account the world information above and the error message and write the new one below.
                Write a numbered list where each line corresponds to a single task.
                Each task should a single, concise sentence, and be achievable using the functions walk and interact.
            ''')
        elif not plan:
            what = "no plan"
            prompt = self.sanitize(f'''
                You have completed your plan but you still haven't achieved your final goal '{goal}'.
                Reevaluate your plan taking into account the world information above and write the new one below.
                Write a numbered list where each line corresponds to a single task.
                Each task should a single, concise sentence, and be achievable using the functions walk and interact.
            ''')
        else:
            what = "success"
            prompt = self.sanitize(f'''
                Function succeeded. You have completed the task '{plan[0]}'.
                Your final goal is '{goal}'.
                If necessary, reevaluate your plan taking into account the world information above and write the new one below.
                If you do not wish to reevaluate your plan, write the same plan below.
                Write a numbered list where each line corresponds to a single task.
                Each task should a single, concise sentence, and be achievable using the functions walk and interact.
            ''')

        prompt += f'''

            Information about the world (ranked from most to least important):
            """
            {newline.join(context)}
            """
        '''

        result = await openai.ChatCompletion.acreate(
                model=self.model,
                temperature=0.5,
                messages=memory + [{"role": "system", "content": prompt}],
                functions=self.FUNCTIONS)
        content = result["choices"][0]["message"]["content"] # type: ignore

        print()
        print(f"-------- OpenAI {what} response --------")
        print(content)
        print()

        # TODO: validate plan
        return [task.strip() for task in content.split("\n")]
