from app import App
from interactions import Win
from ai import Database, Prompt, AIController

def app(db: Database, prompt: Prompt) -> App:
    app = App((32, 20))
    flag = [False]

    app.add_object_type("goal", Win("hand", "goal", flag))
    app.add_object("goal", "goal", (15, 8))
    app.add_character("red", AIController(db, prompt, "Win.", flag), (5, 5), {"hand"})

    # Random decor
    app.place_decor("tree", (1, 1))
    app.place_decor("tree", (6, 0))
    app.place_decor("tree", (11, 2))
    app.place_decor("tree", (19, 0))
    app.place_decor("tree", (27, 0))
    app.place_decor("tree", (30, 8))
    app.place_decor("tree", (2, 6))
    app.place_decor("tree", (1, 13))
    app.place_decor("tree", (9, 17))
    app.place_decor("tree", (15, 14))
    app.place_decor("tree", (24, 16))

    return app
