from imports import *
from config import CHANNEL_ID
from utils import luikaus
from db import give_points

tracked_message_id_rand = None
handled_reactions_rand = set()

#Niilo lähettää satunnaisia viestejä omatoimisesti klo 9-21 välillä

@tasks.loop(minutes = 1)
async def luikaus_loop(client):
	global tracked_message_id_rand
	rng = random.randint(0,1499)
	hour = datetime.datetime.now().hour
	earliest = 9
	latest = 21
	if  rng == 22 and earliest <= hour and hour <= latest:
		try:
			channel = client.get_channel(CHANNEL_ID)
			msg = await channel.send(luikaus())
			tracked_message_id_rand = msg.id
		except AttributeError:
			print("naps")



def setup_luikaus_loop(client):
	@luikaus_loop.before_loop
	async def before_loop():
		await client.wait_until_ready()

	if not luikaus_loop.is_running():
		luikaus_loop.start(client)

	@client.listen("on_reaction_add")
	async def luikaus_reaction_handler(reaction, user):
		global handled_reactions_rand, tracked_message_id_rand

		if user == client.user:
			return

		if reaction.message.id == tracked_message_id_rand and reaction.message.id not in handled_reactions_rand:
			handled_reactions_rand.add(reaction.message.id)
			await reaction.message.channel.send(f"{user.mention} ansaitsi 5 niilopistettä")
			await give_points(client, user.id, 5)