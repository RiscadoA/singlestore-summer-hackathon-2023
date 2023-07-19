from app import App
from interactions import Open, PickUp, Give
from world import HumanController, ScriptedController, Walk, Ask

def example1() -> App:
    app = App((32, 32))

    # Allow characters to give stuff to each other (but not their hands)
    app.add_interaction("character", Give({"hand"}))

    # Register some object types
    app.add_object_type("door", Open("door", "key"))
    app.add_object_type("key", PickUp("key", "hand"), occlude=False)

    # Make a cliff from the left to the right of the map, with a door in the middle
    for i in range(0, 15):
        app.place_ground("cliff-m", (i, 3))
    app.place_ground("cliff-r", (15, 1))
    app.place_ground("cliff-l", (17, 1))
    for i in range(18, 32):
        app.place_ground("cliff-m", (i, 3))
    app.add_object("door", "door", (16, 5))

    # Add some decorative trees (not as objects)
    app.place_decor("tree", (0, 0))
    app.place_decor("tree", (3, 1))
    app.place_decor("tree", (6, 0))
    app.place_decor("tree", (9, 1))
    app.place_decor("tree", (12, 0))
    app.place_decor("tree", (21, 1))
    app.place_decor("tree", (24, 0))
    app.place_decor("tree", (27, 1))
    app.place_decor("tree", (30, 0))

    # Add some decorative logs
    app.place_decor("log", (3, 8))
    app.place_decor("log", (21, 20))

    # Add a decorative boulder
    app.place_decor("boulder", (29, 11))
    app.place_decor("boulder", (7, 18))

    # Add a player character, with a hand
    app.add_character("red", ScriptedController(), (19, 1))
    app.add_character("green", ScriptedController([
        Ask("blue", "Hi"),
    ]), (12, 21))
    app.add_character("blue", ScriptedController(), (27, 24))
    app.add_character("guy", HumanController(app.console), (0, 2), {"hand"})

    # Add a key and a goal
    app.add_object("key", "key", (31, 2))
    app.add_object("goal", "goal", (15, 10))

    return app

if __name__ == "__main__":
    example1().run()
