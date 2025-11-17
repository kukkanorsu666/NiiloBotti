from .points import setup_points
from .luikaus import setup_luikaus
from .achievements import setup_achievements

def setup_commands(client):
    setup_points(client)
    setup_luikaus(client)
    setup_achievements(client)
    print("Commands init done")