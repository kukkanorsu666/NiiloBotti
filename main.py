from imports import *
from config import BOT_TOKEN
from tasks import setup_tasks
from commands import setup_commands

intents = disnake.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
	print("Valmis")

if __name__ == "__main__":
	setup_commands(client)
	setup_tasks(client)
	client.run(BOT_TOKEN)
