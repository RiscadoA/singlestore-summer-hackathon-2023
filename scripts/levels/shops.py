from app import App
from interactions import Win, PickUp, Open, Shop
from ai import Database, Prompt, AIController

def app(db: Database, prompt: Prompt) -> App:
    app = App((32, 20))
    flag = [False]

    # Register some object types
    app.add_object_type("goal", Win("hand", "goal", flag))
    app.add_object_type("door", Open("door", "key"))
    app.add_object_type("green-box", Shop("green-box", "shrubbery", "money"))
    app.add_object_type("yellow-box", Shop("yellow-box", "money", "key"))
    app.add_object_type("shrubbery", PickUp("shrubbery", "hand"), occlude=False)

    # Make a cliff from the left to the right of the map, with a door in the middle
    for i in range(0, 15):
        app.place_ground("cliff-m", (i, 6))
    app.place_ground("cliff-r", (15, 4))
    app.place_ground("cliff-l", (17, 4))
    for i in range(18, 32):
        app.place_ground("cliff-m", (i, 6))
    app.add_object("door", "door", (16, 8))

    app.add_object("goal", "goal", (15, 15))
    app.add_object("shrubbery", "shrubbery", (5, 4))
    app.add_object("yellow-box", "yellow-box", (10, 4))
    app.add_object("green-box", "green-box", (21, 4))
    app.add_character("red", AIController(db, prompt, "Win.", flag), (1, 1), {"hand"})

    return app
