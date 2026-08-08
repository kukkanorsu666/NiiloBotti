from imports import *
from config import CHANNEL_ID, SERVER_ID
from db import give_points, give_points_daily
from utils import ai_summary, daily, check_achievements, get_total_reactions, add_reaction, update_reaction_streak_logic
from commands.niilokortit import change_boosterpack_amount

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
			try:
				await give_points_daily(client)
				channel = client.get_channel(CHANNEL_ID)

				video_url = await asyncio.to_thread(daily)
				if video_url is None:
					await channel.send("Ei löytynyt tämän päivän videota.")
					return

				try:
					summary = await asyncio.to_thread(ai_summary, video_url)
					msg = await channel.send("_" + summary + "_" + "\n" + video_url)
				except Exception as e:
					print(e)
					msg = await channel.send("Napsahti että pärähti! (" + str(e) + ")" + "\n" + video_url)

				tracked_message_id = msg.id
			except Exception as e:
				print(f"daily_loop failed: {e}")


	@daily_loop.before_loop
	async def before_daily_loop():
		await client.wait_until_ready()

	daily_loop.start()




#Antaa 5 niilopistettä ensimmäiselle joka reagoi päivän videoon
@client.listen("on_reaction_add")
async def daily_reaction_handler(reaction, user):
	global handled_reactions

	if user == client.user:
		return

	if reaction.message.id == tracked_message_id and reaction.message.id not in handled_reactions:
		handled_reactions.add(reaction.message.id)
		random_number = random.randint(1,3)
		if random_number == 1:
			await change_boosterpack_amount(user.id, 1)
			await reaction.message.channel.send(f"{user.mention} Ansaitsi 5 niilopistettä ja löysi korttipakan!")
		else:
			await reaction.message.channel.send(f"{user.mention} Ansaitsi 5 niilopistettä")
		await give_points(client, user.id, 5)
		


		await add_reaction(user.id, 1)
		total_reactions = await get_total_reactions(user.id)
		await check_achievements(client, user.id, 'reaction_wins_10', total_reactions)
		await check_achievements(client, user.id, 'reaction_wins_30', total_reactions)
		await check_achievements(client, user.id, 'reaction_wins_50', total_reactions)
		streak = await update_reaction_streak_logic(user.id, user.id)
		await check_achievements(client, user.id, "reaction_streak_3", streak)
		await check_achievements(client, user.id, "reaction_streak_7", streak)