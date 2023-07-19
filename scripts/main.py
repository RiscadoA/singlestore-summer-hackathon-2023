import levels
import os
import dotenv

from ai.database import DumbDatabase
from ai.prompt import HumanPrompt

if __name__ == "__main__":
    dotenv.load_dotenv()
    level = os.getenv("LEVEL", "pickup_and_open")
    db = DumbDatabase()
    prompt = HumanPrompt()
    levels.app(level, db, prompt).run()
