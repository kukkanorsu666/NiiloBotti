from .points import setup_points
from .luikaus import setup_luikaus
from .achievements import setup_achievements
from .niilokortit import setup_niilokortit, setup_open_boosterpack, setup_buy_boosterpack

def setup_commands(client):
    setup_points(client)
    setup_luikaus(client)
    setup_achievements(client)
    setup_niilokortit(client)
    setup_open_boosterpack(client)
    setup_buy_boosterpack(client)
    print("Commands init done")