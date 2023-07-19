import levels
import os
import dotenv

from ai.database import DumbDatabase
from ai.prompt import HumanPrompt, OpenAIPrompt

if __name__ == "__main__":
    dotenv.load_dotenv()
    level = os.getenv("LEVEL", "pickup_and_open")
    db = os.getenv("DATABASE", "s2")
    prompt = os.getenv("PROMPT", "openai")

    if db == "s2":
        raise NotImplementedError("SingleStore database not implemented yet")
    elif db == "dumb":
        db = DumbDatabase()
    else:
        raise ValueError(f"Invalid database '{db}': must be either 's2' or 'dumb'")

    if prompt == "openai":
        key = os.getenv("OPENAI_API_KEY")
        assert key is not None, "OPENAI_API_KEY must be set to use the OpenAI prompt"
        prompt = OpenAIPrompt(
            api_key=key,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    elif prompt == "human":
        prompt = HumanPrompt()
    else:
        raise ValueError(f"Invalid prompt '{prompt}': must be either 'openai' or 'human'")

    levels.app(level, db, prompt).run()
