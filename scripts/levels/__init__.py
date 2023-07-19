from app import App

def app(name: str) -> App:
    """Starts the game"""
    return __import__(name, globals(), locals(), level=1).app()
