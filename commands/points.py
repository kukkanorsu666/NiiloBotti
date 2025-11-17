from imports import *
from db import fetch_points
from config import *
from utils import check_achievements, lotto, pay_bet

def setup_points(client):
	#Botti kertoo kuinka monta niilopistettä käyttäjällä on
	@client.slash_command(name = "niilopisteet", description = "Näe niilopisteesi", guild_ids=[SERVER_ID])
	async def pisteetcom(interaction: disnake.ApplicationCommandInteraction):
		user_id = interaction.user.id
		points = await fetch_points(user_id)
		await interaction.response.send_message(F"Sulla on {points} niilopistettä")

	#Käyttäjä voi pelata hedelmäpeliä asettamalla panoksen
	@client.slash_command(name = "lotto", description = "voe morjesta", guild_ids=[SERVER_ID])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def lottocom(interaction: disnake.ApplicationCommandInteraction,
		panos: int = None):
		
		await interaction.response.defer(ephemeral=False)

		current_points = await fetch_points(interaction.user.id)
		channel = client.get_channel(CHANNEL_ID)
		user_id = interaction.user.id

		if panos is None or panos <= 0:
			await check_achievements(client, user_id, 'gamble_with_0', 1)
			await interaction.followup.send("Ei tätä ilmatteeks pelata")
		elif current_points < panos:
			await interaction.followup.send("https://tenor.com/view/niilo-niilo22-mene-toihin-mee-gif-8148789")
		else:
			await lotto(client, interaction, interaction.user.mention, interaction.user.id, panos)
			await pay_bet(client, interaction.user.id, panos)

	@lottocom.error
	async def lotto_error(interaction: disnake.ApplicationCommandInteraction, error):
		if isinstance(error, commands.CommandOnCooldown):
			retry_after = int(error.retry_after)
			await interaction.response.send_message(f"oot jäähyllä {retry_after} sekunttia", ephemeral=True)
		else:
			raise error