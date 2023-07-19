from app import App
from ai import Database, Prompt

def app(name: str, db: Database, prompt: Prompt) -> App:
    """Returns the app for the given level"""
    app = __import__(name, globals(), locals(), level=1).app(db, prompt)
    db.fill(app.world)
    return app
