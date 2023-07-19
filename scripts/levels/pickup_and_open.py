from app import App
from state import State
from vector.embedding import EmbeddingTools
from vector.completion import CompletionTools
from interactions import Open, PickUp, Give
from world import HumanController, ScriptedController, AIController, Walk, Ask

def app(embedding: EmbeddingTools, completion: CompletionTools) -> App:
    app = App((32, 32))

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

    # Add a key and a goal
    app.add_object("key", "key", (31, 2))
    app.add_object("goal", "goal", (15, 10))

    # Create the state to put in the controllers
    app_context = app.get_context()

    inventory = [
    ]

    rules = (
        "trees can be chopped down with axes and drop wood\n"
    )
    for rule in app_context["Rules"]:
        rules += rule + "\n"

    objects = ""
    for obj in app_context["Objects"]:
        objects += obj + "\n"

    context = (
        f"there are trees 'tree'\n"
        f"you have the following items: "
    )

    goal = "eat food"

    state = State(embedding, completion, inventory, rules, objects, context, goal)
    state.generate_embeddings_from_rules()
    state.put_items_in_db()

    # Add an AI character, with a hand
    app.add_character("red", AIController(app.console, state), (19, 1), {"hand"})

    return app
