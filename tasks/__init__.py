from .live import setup_live_tasks
from .luikaus_loop import setup_luikaus_loop
from .daily import setup_daily

def setup_tasks(client):
    setup_live_tasks(client)
    setup_luikaus_loop(client)
    setup_daily(client)
    print("Tasks init done")