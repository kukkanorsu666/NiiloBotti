from .points import setup_points
from .luikaus import setup_luikaus

def setup_commands(client):
    setup_points(client)
    setup_luikaus(client)
    print("Commands init done")