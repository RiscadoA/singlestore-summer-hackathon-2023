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
        )

        # print("Full response:")
        # print(result)

        return result["choices"][0]["message"]["content"]
