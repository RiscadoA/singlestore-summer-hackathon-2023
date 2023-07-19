from app import App
from interactions import Win
from ai import Database, Prompt, AIController

def app(db: Database, prompt: Prompt) -> App:
    app = App((32, 32))

    flag = [False]
    app.add_object_type("goal", Win("hand", "goal", flag))
    app.add_object("goal", "goal", (15, 15))
    app.add_character("red", AIController(db, prompt, "win", flag), (5, 5), {"hand"})

    return app
