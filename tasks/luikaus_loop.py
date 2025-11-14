from imports import *
from config import CHANNEL_ID
from utils import luikaus

#Niilo lähettää satunnaisia viestejä omatoimisesti klo 9-21 välillä
@tasks.loop(minutes = 1)
async def luikaus_loop(client):
	rng = random.randint(0,1500)
	hour = datetime.datetime.now().hour
	earliest = 9
	latest = 21
	if  rng == 22 and earliest <= hour and hour <= latest:
		try:
			channel = client.get_channel(CHANNEL_ID)
			await channel.send(luikaus())
		except AttributeError:
			print("naps")

def setup_luikaus_loop(client):
	@luikaus_loop.before_loop
	async def before_loop():
		await client.wait_until_ready()

	luikaus_loop.start(client)