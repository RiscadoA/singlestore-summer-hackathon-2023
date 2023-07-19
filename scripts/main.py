import argparse
import levels
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts the game")
    parser.add_argument("level", nargs="?", default="pickup_and_open", help="The level to start")
    args = parser.parse_args()
    levels.app(args.level).run()
