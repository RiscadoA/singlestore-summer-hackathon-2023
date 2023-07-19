from app import App
from vector.connector import DatabaseConnector
from vector.embedding import EmbeddingTools
from vector.completion import CompletionTools

def app(name: str) -> App:
    """Starts the game"""
    conn = DatabaseConnector()
    embedding = EmbeddingTools(conn)
    completion = CompletionTools()

    return __import__(name, globals(), locals(), level=1).app(embedding, completion)
