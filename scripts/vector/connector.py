import singlestoredb as s2
import os


class DatabaseConnector:
    """Connector for the database to run queries against it. Uses S2 connector."""

    def __init__(self):
        super().__init__()
        self._id = -1
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

    def run_query(self, query):
        with self._conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        return results
