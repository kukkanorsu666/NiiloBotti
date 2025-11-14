from imports import *
from config import CHANNEL_ID, SERVER_ID
from db import give_points, give_points_daily
from utils import ai_summary, daily

tracked_message_id = None
handled_reactions = set()

def setup_daily(client):
	#Lähettää uusimman Niilon videon päivittäin klo 16
	@tasks.loop(minutes=1)
	async def daily_loop():
		x = datetime.time(16, 0)
		scheduled_time_hour = x.hour
		scheduled_time_minute = x.minute

		global tracked_message_id

		if scheduled_time_hour  == datetime.datetime.now().hour and scheduled_time_minute == datetime.datetime.now().minute:
			await give_points_daily(client)
			channel = client.get_channel(CHANNEL_ID)
			attempt = 0
			for x in range(0, 2):
				try:
					msg = await channel.send("_" + ai_summary() + "_" + "\n" + daily())
					tracked_message_id = msg.id
					err = None
						
				except Exception as e:
					print(e)
					if attempt == 1:
						msg = await channel.send("Napsahti että pärähti! (" + err + ")" + "\n" + daily())
						tracked_message_id = msg.id
						break
					err = str(e)
					attempt += 1
					print(f"#{attempt} - {err}")
				if err:
					await sleep(2)
				else:
					break
	

	@daily_loop.before_loop
	async def before_daily_loop():
		await client.wait_until_ready()

	daily_loop.start()				




	#Antaa 5 niilopistettä ensimmäiselle joka reagoi päivän videoon
	@client.event
	async def on_reaction_add(reaction, user):
		global handled_reactions

		if user == client.user:
			return

		if reaction.message.id == tracked_message_id and reaction.message.id not in handled_reactions:
			handled_reactions.add(reaction.message.id)
			await reaction.message.channel.send(f"{user.mention} ansaitsi 5 niilopistettä")
			await give_points(user.id, 5)