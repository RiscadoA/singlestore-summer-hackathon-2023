import json
import openai
import os
from dotenv import load_dotenv

from vector.connector import DatabaseConnector
from vector.embedding import EmbeddingTools
from vector.completion import CompletionTools

from scripts.main import App

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

conn = DatabaseConnector()
embedding = EmbeddingTools(conn)
completion = CompletionTools()


def handle_result(result, inventory, context):
    parses = json.loads(result)
    obj = parses["objects"][0]

    if parses["action"] == "move":
        return inventory, f"You are next to {obj}"

    elif parses["action"] == "interact":
        if len(parses["objects"]) != 2:
            return inventory, "Not enough arguments for 'interact' action"

        if obj not in inventory:
            return inventory, f"You do not have {obj}"

        iv = parses["objects"][1]
        response = f"You used {obj} on {iv}"
        if obj == "axe" and iv == "tree":
            inventory += [
                "wood",
            ]
            response += " and now you have wood"
        return inventory, response

    elif parses["action"] == "pickup":
        flag = False
        for el in context:
            if obj in el:
                flag = True

        if flag:
            inventory += [
                obj,
            ]
            return inventory, f"You now have {obj}"
        else:
            return inventory, f"There is no {obj} to pickup"

    return None, None


def main():
    # create table
    conn.run_query(
        """
        CREATE TABLE IF NOT EXISTS info(
            id INT not null PRIMARY KEY,
            context TEXT,
            vector blob
        );
        """
    )
    conn.run_query("DELETE FROM info;")  # TODO might delete this later


if __name__ == "__main__":
    main()
