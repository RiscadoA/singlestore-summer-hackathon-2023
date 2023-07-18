import json
import openai
import os
from dotenv import load_dotenv

from vector.connector import DatabaseConnector
from vector.embedding import EmbeddingTools
from vector.completion import CompletionTools

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
            inventory += ["wood",]
            response += " and now you have wood"
        return inventory, response

    elif parses["action"] == "pickup":

        flag = False
        for el in context:
            if obj in el:
                flag = True

        if flag:
            inventory += [obj,]
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

    initial_prompt = (
            'You are an assistant that only speaks JSON. Do NOT write normal text.\n'
            'The format is as follows:\n'
            '{\n'
            '  "action": // one of "move", "interact", "pickup"\n'
            '  "objects": // for "move" and "pickup": one element array. for "interact", [obj1, obj2] ("use <obj1> on <obj2>")\n'
            '  "goals": // queue: in decreasing order of immediance. You can only push and pop one element at a time.\n'
            '}\n'
            )

    inventory = ["axe",]

    rules = (
            "trees can be chopped down with axes and drop wood\n"
            "you can eat the item you are holding by interacting with ['mouth', food]\n"
            "the shop 'appleShop' sells 'apples' in exchange for 'money'\n"
            "the shop 'woodShop' buys 'wood' in exchange for 'money'\n"
            )

    context = (
            f"there are trees 'tree'\n"
            f"there are shops 'appleShop' and 'woodShop'\n"
            f"you have the following items: "
            )

    goal = "eat food"

    answer_restriction = (
            "please answer with one and only one action at a time (like the game the oregon trail), and add intermediate goals"
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
        # prompt = (
                # f"{initial_prompt}\n"
        prompt = (
                f"# Rules\n"
                f"{newline.join(embedding.semantic_search(goal, limit=2))}\n\n"
                f"# Context\n{context}{', '.join(inventory)}\n"
                f"your goal is: {goal}\n\n"
                f"# Previous actions\n{lastActions}\n"
                f"{answer_restriction}\n\n"
                f"# Last response\n"
                f"{response}"
                )
        print(prompt)

        result = completion.prompt([prompt])
        print("\n=> RESULT: " + result["message"] + "\n")

        if result.get("function_call"):
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "move": None, # TODO this
                "pickup": None, # TODO this
                "interact": None, # TODO this
            }  # only one function in this example, but you can have multiple
            function_name = result["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(result["function_call"]["arguments"])
            if function_name == "interact":
                function_response = function_to_call(
                    obj1=function_args.get("obj1"),
                    obj2=function_args.get("obj2"),
                )
            else:
                function_response = function_to_call(
                    obj=function_args.get("obj"),
                )

        # TODO this will be removed (?)
        inventory, response = handle_result(result["message"], inventory, context)

        lastActions += result + "\n"

        i += 1
        input()


if __name__ == "__main__":
    main()
