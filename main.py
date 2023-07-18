import json
import openai
import os
from dotenv import load_dotenv

from connector import DatabaseConnector
from embedding import EmbeddingTools
from completion import CompletionTools

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

conn = DatabaseConnector()
embedding = EmbeddingTools(conn)
completion = CompletionTools()


def handle_result(result, inventory, context):
    parse = json.loads(result)

    if parse["action"] == "move":
        return inventory, f"You are next to {parse['objects'][0]}"

    elif parse["action"] == "interact":
        iv = parse["objects"][1]
        if iv not in inventory:
            return inventory, f"You do not have {iv}"

        return inventory, f"You used {parse['objects'][0]} on {iv}"

    elif parse["action"] == "pickup":
        obj = parse["objects"][0]

        flag = False
        for el in context:
            if obj in el:
                flag = True

        if flag:
            inventory += [obj,]
            return inventory, f"You now have {obj}"
        else:
            return inventory, f"There is no {obj} to pickup"

    return inventory, None

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

    initial_prompt = (
            'You are an assistant that only speaks JSON. Do NOT write normal text.\n'
            'The format is as follows:\n'
            '{\n'
            '  "action": // one of "move", "interact", "pickup"\n'
            '  "objects": // array: needs one element for "move" and "pickup", and two elements for "interact"\n'
            '  "goals": // array: from more immediate goal to less imediate goal. You can create new goals as you see fit.\n'
            '}\n'
            )

    inventory = ["axe",]

    rules = (
            "trees can be chopped down with axes and drop wood\n"
            "you can eat the item you are holding by interacting with 'mouth'\n"
            "the shop 'appleShop' sells 'apples' in exchange for 'money'\n"
            "the shop 'woodShop' buys 'wood' in exchange for 'money'\n"
            )

    context = (
            f"there are trees 'tree'\n"
            f"there are shops 'appleShop' and 'woodShop'\n"
            f"you have the following items: {', '.join(inventory)}"
            )

    goal = "eat food"

    answer_restriction = (
            "please answer with one and only one action at a time (like the game the oregon trail)"
    )

    data = embedding.clean_data(rules)
    vectors = embedding.get_embeddings(data)

    # insert data in the db
    query = """INSERT INTO info VALUES """
    for ctx, vector in zip(data, vectors):
        query += f"""({conn.new_id()}, "{ctx}", JSON_ARRAY_PACK('{vector}')),"""
    query = query[:-1] + ";"

    conn.run_query(query)

    # see inserted content in db:
    # SELECT id, context, JSON_ARRAY_UNPACK(vector) FROM info;

    newline = "\n"
    lastActions = ""
    response = ""

    i = 0
    while i != 20:
        prompt = (
                f"{initial_prompt}\n"
                f"# Rules\n"
                f"{newline.join(embedding.semantic_search(goal, limit=2))}\n\n"
                f"# Context\n{context}\n"
                f"your goal is: {goal}\n\n"
                f"# Previous actions\n{lastActions}\n"
                f"{answer_restriction}\n\n"
                f"# Last response\n"
                f"{response}"
                )
        print(prompt)

        result = completion.prompt([prompt])
        print("\n=> RESULT: " + result + "\n")

        inventory, response = handle_result(result, inventory, context)

        lastActions += result + "\n"

        i += 1
        input()


if __name__ == "__main__":
    main()
