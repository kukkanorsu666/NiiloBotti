from imports import *
from db import *
from utils import *
from config import *
from PIL import Image

def setup_achievements(client):
	
	@client.slash_command(name = "akit", description = "Aiiiaiiiaiiiii", guild_ids=[SERVER_ID])
	async def akkicom(interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
		user = user or interaction.author
		await interaction.response.defer()
		await show_achievements(client, user.id, user)
		achievements = disnake.File("user_achievements.png")
		await interaction.followup.send(file=achievements)