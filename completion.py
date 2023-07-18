import openai
import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

class CompletionTools:
    def prompt(self, prompt):
        result = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt},
            ],
        )

        print("Full response:")
        print(result)

        return result["choices"][0]["message"].content
