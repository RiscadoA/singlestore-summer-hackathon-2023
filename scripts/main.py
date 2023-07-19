import levels
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Starts the game")
    parser.add_argument("level", nargs="?", default="pickup_and_open", help="The level to start")
    args = parser.parse_args()
    levels.app(args.level).run()
