from vector.completion import CompletionTools
from vector.embedding import EmbeddingTools


class State:
    _answer_restriction = (
        "please answer with one and only one action at a time (like the game the oregon trail), and add intermediate goals\n"
        "only use the functions you have been provided with"
    )

    def __init__(self, embedding: EmbeddingTools, completion: CompletionTools, inventory: list[str], rules: str, objects: str, context: str, goal: str):
        self._embedding = embedding
        self._completion = completion
        self.inventory = inventory
        self.rules = rules
        self.objects = objects
        self.context = context
        self.goal = goal
        self.last_actions = ""
        self.response = ""

    def generate_embeddings_from_rules(self):
        """generate the embeddings for the rules to put in the db"""
        self.data = self._embedding.clean_data(self.rules)
        self.vectors = self._embedding.get_embeddings(self.data)

    def put_items_in_db(self):
        """insert data in the db"""

        query = """INSERT INTO info VALUES """
        for ctx, vector in zip(self.data, self.vectors):
            query += f"""({self._embedding.new_id()}, "{ctx}", JSON_ARRAY_PACK('{vector}')),"""
        query = query[:-1] + ";"

        self._embedding._conn.run_query(query)

        # see inserted content in db:
        # SELECT id, context, JSON_ARRAY_UNPACK(vector) FROM info;

    def generate_prompt(self):
        newline = "\n"
        return (
            f"# Rules\n"
            f"{newline.join(self._embedding.semantic_search(self.goal, limit=2))}\n\n"
            f"# Objects\n{self.objects}\n"
            f"# Context\n{self.context}{', '.join(self.inventory)}\n"
            f"your goal is: {self.goal}\n\n"
            f"# Previous actions\n{self.last_actions}\n"
            f"{self._answer_restriction}\n\n"
            f"# Last response\n"
            f"{self.response}"
        )

    def query_ai(self, prompt):
        return self._completion.prompt([prompt])

    def add_rules(self, rules):
        self.rules += rules

    def update_last_actions(self, new_last_actions):
        self.last_actions = new_last_actions

    def update_response(self, new_response):
        self.response = new_response
