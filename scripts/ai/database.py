import openai
import os
import singlestoredb as s2
from typing import Optional
from world import World

class Database():
    """Interface for the database which stores the context used by the AI.
    The context includes:
    - rules;
    - objects;
    - characters.
    """

    def __init__(self):
        self.world = None
        self.filled = False
        self._id = -1
        self._encoding = os.getenv("ENCODING_NAME", "cl100k_base")
        self._model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self._conn = s2.connect(
            host=os.getenv("S2_DB_HOST", ""),
            port=int(os.getenv("S2_DB_PORT", 0)),
            user=os.getenv("S2_DB_USER", ""),
            password=os.getenv("S2_DB_PASSWORD", ""),
            database=os.getenv("S2_DB_DATABASE", ""),
        )

    def new_id(self):
        self._id += 1
        return self._id

    def get_embedding(self, text):
        """Returns the vector for semantic search, using the OpenAI embedding API"""
        return openai.Embedding.create(input=[text], model=self._model)["data"][0]["embedding"]

    def get_embeddings(self, vector):
        """get_embedding but mapped to a vector of inputs"""
        return list(map(self.get_embedding, vector))

    def fill(self, world: World):
        """Fills the database with data from the given world"""
        context = []
        context += list(map(lambda x: x.rule(), world.interactions.values()))
        context += list(map(lambda id, x: f"There is a '{x.type}' named '{id}'.", world.objects.keys(), world.objects.values()))
        #context += list(map(lambda id: f"There is a character named '{id}'.", world.characters.keys()))

        with self._conn.cursor() as cursor:
            cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS info(
                        id INT not null PRIMARY KEY,
                        context TEXT,
                        vector blob
                        );
                    """
            )
            cursor.execute("DELETE FROM info;")

            query = """INSERT INTO info VALUES """
            for ctx, vector in zip(context, self.get_embeddings(context)):
                query += f"""({self.new_id()}, "{ctx}", JSON_ARRAY_PACK('{vector}')),"""
            query = query[:-1] + ";"
            cursor.execute(query)

        self.filled = True


    def query(self, task: str, error: Optional[str] = None) -> list[str]:
        """Queries context for the given task, optionally with the error message of the previous action if it failed"""
        assert self.filled, "Database must be filled before querying"

        goal_vector = self.get_embedding(task)

        context_filtered = []

        with self._conn.cursor() as cursor:
            cursor.execute(
                f"""
                    SELECT id, context, dot_product(vector, JSON_ARRAY_PACK('{goal_vector}')) AS score
                    FROM info
                    ORDER BY score DESC
                    LIMIT 3;
                """
            )
            results = cursor.fetchall()

        for row in results:
            _, filtered, _ = row
            context_filtered += [
                filtered,
            ]

        if error is None:
            context_filtered.append(self.query(error))

        return context_filtered

class DumbDatabase(Database):
    """Dumb database which dumps all of the context to the AI"""

    def __init__(self):
        self.world = None

    def fill(self, world: World):
        self.world = world

    def query(self, task: str, error: Optional[str] = None) -> list[str]:
        assert self.world is not None, "Database must be filled before querying"

        context = []
        context += list(map(lambda x: x.rule(), self.world.interactions.values()))
        context += list(map(lambda id, x: f"There is a '{x.type}' named '{id}'.", self.world.objects.keys(), self.world.objects.values()))
        #context += list(map(lambda id: f"There is a character named '{id}'.", self.world.characters.keys()))
        return context
