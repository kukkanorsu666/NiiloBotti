from imports import *
from db import *
from utils import *
from config import *

def setup_luikaus(client):
	#Lähettää satunnaisen luikauksen luikaukset.txt tiedostosta
	@client.slash_command(name = "luikaus", description = "Ei siitä sen enempää", guild_ids=[SERVER_ID])
	async def luikauscom(
		interaction: disnake.ApplicationCommandInteraction,
		numero: Optional[int] = None):

		if numero is None or numero > 195 or numero < 0:
			await interaction.response.send_message(luikaus())

		else:
			await interaction.response.send_message(valittuluikaus(numero))


	#Lähettää satunnaisen gifin gif kansiosta
	@client.slash_command(name = "pätkä", description = "Ei siitä sen enempää", guild_ids=[SERVER_ID])
	async def gifucom(interaction: disnake.ApplicationCommandInteraction):
		await interaction.response.send_message(gifu())


	#Lähettää satunnaisen videon videot.txt tiedostosta
	@client.slash_command(name = "video", description = "Tästä videoustia", guild_ids=[SERVER_ID])
	async def videocom(interaction: disnake.ApplicationCommandInteraction):
		await interaction.response.send_message((video()))




	#Komento jolla Niilo tulee puheluun kertomaan päivästää
	@client.command(pass_context = True)
	async def n(ctx):
		if(ctx.author.voice):
			channel = ctx.message.author.voice.channel
			print(channel, ctx.author)
			voice = await channel.connect(reconnect = True)
			chosen_voice = voice_path_wav + random_voice()
			source = FFmpegPCMAudio(chosen_voice)
			player = voice.play(source)
			while voice.is_playing():
				await sleep(1)
			await voice.disconnect()

		else:
			
			await ctx.send("Mee kanavalle saatana")


	@client.command(pass_context = True)
	async def leave(ctx):
		if (ctx.voice_client):
			await ctx.guild.voice_client.disconnect()