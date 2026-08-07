from imports import *
from config import BOT_TOKEN
from tasks import setup_tasks
from commands import setup_commands

import logging
logging.basicConfig(
	filename="voice_debug.log",
	filemode="a",
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("disnake.voice_client").setLevel(logging.DEBUG)
logging.getLogger("disnake.gateway").setLevel(logging.DEBUG)



@client.event
async def on_ready():
	
	print("Valmis")

if __name__ == "__main__":
	setup_commands(client)
	setup_tasks(client)

	client.run(BOT_TOKEN)