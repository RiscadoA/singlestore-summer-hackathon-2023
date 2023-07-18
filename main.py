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

    rules = """
    trees can be chopped down with axes and drop wood
    you can eat the item you are holding by interacting with "mouth"
    the shop "appleShop" sells "apples" in exchange for "money"
    the shop "woodShop" buys "wood" in exchange for "money"
    """

    context = """
    there are trees "tree"
    you have an axe
    """

    goal = "eat food"

    actions = """
    move(object)
    interact(object, object)
    pickup(object)
    """

    answer_restriction = """
    please answer with one and only one action at a time (like the game the oregon trail)
    """

    # information = """
    # there is a tree blocking the path from A to B
    # there is an axe at A
    # you can cut down trees with an axe
    # """

    data = embedding.clean_data(rules + context)
    vectors = embedding.get_embeddings(data)

    # insert data in the db
    query = """INSERT INTO info VALUES """
    for context, vector in zip(data, vectors):
        query += f"""({conn.new_id()}, "{context}", JSON_ARRAY_PACK('{vector}')),"""
    query = query[:-1] + ";"

    conn.run_query(query)

    # see inserted content in db:
    # SELECT id, context, JSON_ARRAY_UNPACK(vector) FROM info;

    # info_filter = embedding.semantic_search(goal, limit=3)
    # {", ".join(info_filter)}

    prompt = f"""
    # Rules
    {rules}
    # Context
    {context}
    your goal is: {goal}

    # Actions {actions} {answer_restriction}
    """
    print(prompt)

    result = completion.prompt([prompt])
    print(result)


if __name__ == "__main__":
    main()
