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
            "You are an assistant that only speaks JSON. Do NOT write normal text.\n"
            "The format is as follows:\n"
            "{\n"
            "  'action': // one of 'move', 'interact', 'pickup'\n"
            "  'objects': // array: one element for 'move' and 'pickup', two for 'interact'\n"
            "}\n"
            )

    rules = (
            "trees can be chopped down with axes and drop wood\n"
            "you can eat the item you are holding by interacting with 'mouth'\n"
            "the shop 'appleShop' sells 'apples' in exchange for 'money'\n"
            "the shop 'woodShop' buys 'wood' in exchange for 'money'\n"
            )

    context = (
            "there are trees 'tree'\n"
            "you have an axe\n"
            )

    goal = "eat food"

    actions = (
            "move(object)\n"
            "interact(object, object)\n"
            "pickup(object)\n"
            )

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

    i = 0
    while i != 2:
        prompt = (
                f"{initial_prompt}\n"
                f"# Rules\n"
                f"{newline.join(embedding.semantic_search(goal, limit=3))}\n\n"
                f"# Context\n{context}\n"
                f"your goal is: {goal}\n\n"
                f"# Previous actions\n{lastActions}\n"
                f"# Actions\n{actions}\n"
                f"{answer_restriction}"
                )
        print(prompt)

        result = completion.prompt([prompt])
        print("RESULT: " + result)

        lastActions += result + "\n"

        i += 1


if __name__ == "__main__":
    main()
