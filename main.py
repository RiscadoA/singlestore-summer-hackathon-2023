import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

def main():
  openai.api_key = OPENAI_API_KEY

  information = """
    there is a tree blocking the path from A to B
    there is an axe at A
    you can cut down trees with an axe
  """

  goal = "get from A to B"

  prompt = f"""
    Your goal is "{goal}".
    Write the steps to achieve your goal.
    Information about the world:
    {information}
  """

  result = openai.ChatCompletion.create(
    model=OPENAI_MODEL,
    messages=[
          {"role": "system", "content": prompt},
      ]
  )

  print("Full response:")
  print(result)
  print("Text response:")
  print(result.choices[0].message.content)

if __name__ == "__main__":
  main()
