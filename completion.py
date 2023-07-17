import openai
import os
import tiktoken

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
ENCODING_NAME = os.getenv("ENCODING_NAME", "cl100k_base")

class CompletionTools:
    _encoding = ENCODING_NAME

    def num_tokens_from_string(self, string):
        """Returns the number of tokens in a text string"""
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        num_tokens = len(encoding.encode(string))
        return num_tokens

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
