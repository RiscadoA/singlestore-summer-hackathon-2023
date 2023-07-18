import openai
import os
import tiktoken

class EmbeddingTools():
    _encoding = os.getenv("ENCODING_NAME", "cl100k_base")
    _model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

    def __init__(self, conn):
        super().__init__()
        self._conn = conn

    def clean_data(self, data):
        """Gets a string of input, splits newlines, strips whitespace, avoids empty strings"""
        return [el.strip() for el in data.split("\n") if el.strip() != ""]

    def get_embedding(self, text):
        """Returns the vector for semantic search, using the OpenAI embedding API"""
        return openai.Embedding.create(input=[text], model=self._model)["data"][0]["embedding"]

    def get_embeddings(self, vector):
        """get_embedding but mapped to a vector of inputs"""
        return list(map(self.get_embedding, vector))

    def num_tokens_from_string(self, string):
        """Returns the number of tokens in a text string"""
        encoding = tiktoken.get_encoding(self._encoding)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def semantic_search(self, query, limit=3):
        """Using the SingleStore connector, see phrases that are related to the one we are searching for"""
        goal_vector = self.get_embedding(query)

        info_filter = []

        results = self._conn.run_query(
            f"""
                SELECT id, context, dot_product(vector, JSON_ARRAY_PACK('{goal_vector}')) AS score
                FROM info
                ORDER BY score DESC
                LIMIT {limit};
            """
        )

        for row in results:
            _, filtered, _ = row
            info_filter += [
                filtered,
            ]

        return info_filter
