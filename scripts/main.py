import dotenv
import levels
import os

from ai.database import SingleStoreDatabase, DumbDatabase
from ai.prompt import HumanPrompt, OpenAIPrompt

if __name__ == "__main__":
    dotenv.load_dotenv()
    level = os.getenv("LEVEL", "pickup_and_open")
    db = os.getenv("DATABASE", "s2")
    prompt = os.getenv("PROMPT_SOURCE", "openai")

    if db == "s2":
        encoding = os.getenv("ENCODING_NAME", "cl100k_base")
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        host = os.getenv("S2_DB_HOST", "")
        port = int(os.getenv("S2_DB_PORT", 0))
        user = os.getenv("S2_DB_USER", "")
        password = os.getenv("S2_DB_PASSWORD", "")
        database = os.getenv("S2_DB_DATABASE", "")
        db = SingleStoreDatabase(encoding, model, host, port, user ,password, database)
    elif db == "dumb":
        db = DumbDatabase()
    else:
        raise ValueError(f"Invalid database '{db}': must be either 's2' or 'dumb'")

    if prompt == "openai":
        key = os.getenv("OPENAI_API_KEY")
        assert key is not None, "OPENAI_API_KEY must be set to use the OpenAI prompt"
        prompt = OpenAIPrompt(
            api_key=key,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
    elif prompt == "human":
        prompt = HumanPrompt()
    else:
        raise ValueError(f"Invalid prompt '{prompt}': must be either 'openai' or 'human'")

    levels.app(level, db, prompt).run()
