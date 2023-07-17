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

    information = """
    there is a tree blocking the path from A to B
    there is an axe at A
    you can cut down trees with an axe
    """

    data = embedding.clean_data(information)
    vectors = embedding.get_embeddings(data)

    # insert data in the db
    query = """INSERT INTO info VALUES """
    for context, vector in zip(data, vectors):
        query += f"""({conn.new_id()}, "{context}", JSON_ARRAY_PACK('{vector}')),"""
    query = query[:-1] + ";"

    conn.run_query(query)

    # see inserted content in db:
    # SELECT id, context, JSON_ARRAY_UNPACK(vector) FROM info;

    # get information from the db, with the goal as the query
    goal = "get from A to B"

    info_filter = embedding.semantic_search(goal, limit=3)

    prompt = f"""
    Your goal is "{goal}".
    Write the steps to achieve your goal.
    Information about the world:
    {", ".join(info_filter)}
    """
    print(prompt)

    result = completion.prompt(prompt)
    print(result)


if __name__ == "__main__":
    main()
