from imports import *
from config import BOT_TOKEN
from tasks import setup_tasks, setup_luikaus_loop
from commands import setup_commands



@client.event
async def on_ready():
	
	print("Valmis")

if __name__ == "__main__":
	setup_commands(client)
	setup_tasks(client)
	setup_luikaus_loop(client)
	client.run(BOT_TOKEN)