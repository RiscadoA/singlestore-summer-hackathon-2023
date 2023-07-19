from app import App
from vector.connector import DatabaseConnector
from vector.embedding import EmbeddingTools
from vector.completion import CompletionTools

def startup(conn: DatabaseConnector):
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

    # delete all elements from the table
    conn.run_query("DELETE FROM info;")

def app(name: str) -> App:
    """Starts the game"""
    conn = DatabaseConnector()
    embedding = EmbeddingTools(conn)
    completion = CompletionTools()
    startup(conn)

    return __import__(name, globals(), locals(), level=1).app(embedding, completion)
