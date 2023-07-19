import openai
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

class CompletionTools:

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def __completion_with_backoff(self, **kwargs):
        return openai.ChatCompletion.create(**kwargs)

    def prompt(self, prompts):
        result = self.__completion_with_backoff(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": prompt} for prompt in prompts],
                functions = [
                    {
                        "name": "move",
                        "description": "move the agent to other position (near a given object)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "object": {
                                    "type": "string",
                                    "description": "the name of the object to move to",
                                },
                            },
                        "required": ["obj"],
                        },
                    },
                    {
                        "name": "interact",
                        "description": "move the agent to other position (near a given object)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "obj1": {
                                    "type": "string",
                                    "description": "the name of the object to use",
                                },
                                "obj2": {
                                    "type": "string",
                                    "description": "the name of the object where object1 will be used",
                                },
                            },
                        "required": ["obj1", "obj2"],
                        },
                    },
                    {
                        "name": "pickup",
                        "description": "get the agent to pickup an object (might move to it)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "obj": {
                                    "type": "string",
                                    "description": "the name of the object to pickup",
                                },
                            },
                        "required": ["obj"],
                        },
                    }
                ]
            )

        return result["choices"][0]["message"]
