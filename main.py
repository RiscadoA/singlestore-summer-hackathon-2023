import openai
import os
import singlestoredb as s2
from dotenv import load_dotenv
from gensim.models import Word2Vec
import numpy as np

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

id = 0

def train_model(data: list[str]):
  clean = [elem.lower().split() for elem in data]
  model = Word2Vec(clean, vector_size=100, window=5, min_count=1, workers=4)
  return model

def string_to_vector(string, model):
  words = string.lower().split()
  vectors = [model.wv[word] for word in words if word in model.wv]
  if vectors:
    return list(np.mean(vectors, axis=0))
  else:
    return None

def get_db():
  return s2.connect(
    host = os.getenv("S2_DB_HOST", ""),
    port = int(os.getenv("S2_DB_PORT", 0)),
    user = os.getenv("S2_DB_USER", ""),
    password = os.getenv("S2_DB_PASSWORD", ""),
    database = os.getenv("S2_DB_DATABASE", ""),
  )

def semantic_search(query, model, db):
  goal_vector = string_to_vector(query, model)

  info_filter = []

  with db.cursor() as cursor:
    cursor.execute(f"""
    SELECT id, context, dot_product(vector, JSON_ARRAY_PACK('{goal_vector}')) AS score
    FROM info
    ORDER BY score DESC
    LIMIT 2;
    """)
    for row in cursor.fetchall():
      _, filtered, _ = row
      info_filter += [filtered,]

  return info_filter

def main():
  global id

  openai.api_key = OPENAI_API_KEY
  db = get_db()

  # create table
  with db.cursor() as cursor:
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS info(
                     id INT not null PRIMARY KEY,
                     context TEXT,
                     vector blob
                     );
                   """)
    cursor.execute("DELETE FROM info;") # TODO might delete this later

  information = """
    there is a tree blocking the path from A to B
    there is an axe at A
    you can cut down trees with an axe
  """

  data = [el.strip() for el in information.split("\n") if el.strip() != ""]
  model = train_model(data)

  vectors = list(map(lambda x: string_to_vector(x, model), data))

  # insert data in the db
  with db.cursor() as cursor:
    for context, vector in zip(data, vectors):
      cursor.execute(f"""INSERT INTO info VALUES ({id}, "{context}", JSON_ARRAY_PACK('{vector}'));""")
      id += 1

  # see in db:
  # SELECT id, context, JSON_ARRAY_UNPACK(vector) FROM info;

  # get information from the db, with the goal as the query
  goal = "get from A to B"

  info_filter = semantic_search(goal, model, db)
  print(info_filter)

  prompt = f"""
    Your goal is "{goal}".
    Write the steps to achieve your goal.
    Information about the world:
    {", ".join(info_filter)}
  """
  print(prompt)

  result = openai.ChatCompletion.create(
    model=OPENAI_MODEL,
    messages=[
          {"role": "system", "content": prompt},
      ]
  )

  print("Full response:")
  print(result)
  print("Text response:")
  print(result.choices[0].message.content)

if __name__ == "__main__":
  main()
