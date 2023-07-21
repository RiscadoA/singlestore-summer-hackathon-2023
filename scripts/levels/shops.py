from app import App
from interactions import Win, PickUp, Open, Shop
from ai import Database, Prompt, AIController

from app import App
from interactions import Open, PickUp, Win
from ai import Database, Prompt, AIController

def app(db: Database, prompt: Prompt) -> App:
    app = App((32, 20))
    flag = [False]

    # Register some object types
    app.add_object_type("goal", Win("hand", "goal", flag))
    app.add_object_type("door", Open("door", "key"))
    app.add_object_type("green-box", Shop("green-box", "shrubbery", "money"))
    app.add_object_type("yellow-box", Shop("yellow-box", "money", "key"))
    app.add_object_type("shrubbery", PickUp("shrubbery", "hand"))

    # Make a cliff from the left to the right of the map, with a door in the middle
    for i in range(0, 15):
        app.place_ground("cliff-m", (i, 5))
    app.place_ground("cliff-r", (15, 3))
    app.place_ground("cliff-l", (17, 3))
    for i in range(18, 32):
        app.place_ground("cliff-m", (i, 5))
    app.add_object("door", "door", (16, 7))

    # Add some decorative trees (not as objects)
    app.place_decor("tree", (0, 1))
    app.place_decor("tree", (3, 0))
    app.place_decor("tree", (6, 2))
    app.place_decor("tree", (9, 1))
    app.place_decor("tree", (12, 0))
    app.place_decor("tree", (21, 2))
    app.place_decor("tree", (24, 3))
    app.place_decor("tree", (27, 1))
    app.place_decor("tree", (30, 1))

    # Add some decorative logs
    app.place_decor("log", (3, 10))
    app.place_decor("log", (21, 17))

    # Add a decorative boulder
    app.place_decor("boulder", (29, 11))
    app.place_decor("boulder", (7, 17))

    # Add a key and a goal
    app.add_object("goal", "goal", (15, 13))
    app.add_object("shrubbery", "shrubbery", (14, 1))
    app.add_object("yellow-box", "yellow-box", (16, 1))
    app.add_object("green-box", "green-box", (20, 1))

    # Add an AI character, with a hand
    app.add_character("red", AIController(db, prompt, "Win.", flag), (19, 3), {"hand"})

    return app
