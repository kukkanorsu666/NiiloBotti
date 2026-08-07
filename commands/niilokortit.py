from imports import *
from config import *
from db import get_db_connection, remove_points, fetch_points
from PIL import Image, ImageFont, ImageDraw
from utils import draw_text_with_rounded_bg


def setup_niilokortit(client):

	#Komento joka näyttää kortit.
	@client.slash_command(name = "kortit", description = "En oo syöny keksiä", guild_ids=[SERVER_ID])
	async def kortticom(interaction: disnake.ApplicationCommandInteraction, user: disnake.User = None):
		user = user or interaction.author
		await interaction.response.defer()
		await show_owned_cards(client, user.id, user)
		await interaction.followup.send(file=disnake.File("user_cards.png"))

cards = [
	("card_mythic_1", "Keksien Rouskuttelija"),
	("card_legendary_2", "Niilo22 X ES"),
	("card_legendary_1", "Lepotilan Legenda"),
	("card_epic_3", "Sitrus-suveraali"),
	("card_epic_2", "Pohjoinen Legioona"),
	("card_epic_1", "Nesteytyksen Näkijä"),
	("card_common_4", "Synkkä Strategi"),
	("card_common_3", "Rautaparta Valvoja"),
	("card_common_2", "Niilopeukku"),
	("card_common_1", "Hiljainen Tarkkailija"),
]

async def get_user_cards(discord_id):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("""
				SELECT card_id, owned, quantity
				FROM user_cards
				WHERE discord_id=%s
			""", (discord_id,))
			rows = {row['card_id']: row for row in await cursor.fetchall()}

	card_data = {}
	for card_id, _ in cards:
		row = rows.get(card_id)
		owned = row['owned'] == 1 if row else False
		quantity = row['quantity'] if row else 0
		card_data[card_id] = {"owned": owned, "quantity": quantity}
	return card_data

card_mapping = {
	":hidden:": Image.open("Niilokortit/hidden.png").resize((500,750)),
	":card_common_1:": Image.open("Niilokortit/common/Hiljainentarkkailija_common.png").resize((500,750)),
	":card_common_2:": Image.open("Niilokortit/common/Niilopeukku_common.png").resize((500,750)),
	":card_common_3:": Image.open("Niilokortit/common/Rautapartavalvoja_common.png").resize((500,750)),
	":card_common_4:": Image.open("Niilokortit/common/Synkkästrategi_common.png").resize((500,750)),
	":card_epic_1:": Image.open("Niilokortit/epic/Nesteytyksennäkijä_epic.png").resize((500,750)),
	":card_epic_2:": Image.open("Niilokortit/epic/pohjoinenlegioona_epic.png").resize((500,750)),
	":card_epic_3:": Image.open("Niilokortit/epic/sitrussuveraali_epic.png").resize((500,750)),
	":card_legendary_1:": Image.open("Niilokortit/legendary/lepotilanlegenda_legendary.png").resize((500,750)),
	":card_legendary_2:": Image.open("Niilokortit/legendary/niilo22xes_legendary.png").resize((500,750)),
	":card_mythic_1:": Image.open("Niilokortit/mythic/keksienrouskuttelija_mythic.png").resize((500,750))
	}


async def show_owned_cards(client,discord_id, user):

	width = 3200
	height = 3500
	background = Image.open("Niilokortit/niilobg.png")

	font1 = ImageFont.truetype("fonts/Play-Bold.ttf", 80)
	font2 = ImageFont.truetype("fonts/Play-Regular.ttf", 24)
	font3 = ImageFont.truetype("fonts/Play-Bold.ttf", 60)
	font4 = ImageFont.truetype("fonts/Play-Regular.ttf", 45)

	rows = [1, 2, 3, 4]

	start_y = 150
	card_spacing_x = 550
	card_spacing_y = 850

	card_index = 0

	cards_unlocked = await get_user_cards(user.id)

	for row_index, cards_in_row in enumerate(rows):

		total_row_width = (cards_in_row ) * card_spacing_x
		start_x = (width - total_row_width) // 2

		y = start_y + (row_index * card_spacing_y)

		for col in range(cards_in_row):
			if card_index >= len(cards):
				break

			card_id, name = cards[card_index]

			#owned = cards_unlocked[card_id]["owned"]
			quantity = cards_unlocked[card_id]["quantity"]
			card_x = start_x + (col * card_spacing_x)

			if quantity:
				card_image = f":{card_id}:"
			else:
				card_image = ":hidden:"

			

			draw_text_with_rounded_bg(
				draw=ImageDraw.Draw(background),
				background=background,
				text=card_image,
				font=font1,
				emoji_mapping=card_mapping,
				last_line_font=font2,
				x=card_x,
				y=y,
				bg_color=(0, 120, 200, 0),
				text_color=(255,255,255),
				radius=12,
				padding=12,
				line_spacing=4
			)

			if quantity > 1:

				badge_x = card_x + 400
				badge_y = y + 700
				draw = ImageDraw.Draw(background)
				draw.rounded_rectangle(
					[(badge_x, badge_y), (badge_x + 140, badge_y + 100)],
					fill=(0,0,0,180),
							radius=18
				)
			
				text = f"x{quantity}"

				bbox = draw.textbbox((0, 0), text, font=font1)
				text_w = bbox[2] - bbox[0]
				text_h = bbox[3] - bbox[1]

				text_x = badge_x + (140 - text_w) // 2
				text_y = badge_y + (80 - text_h) // 2
			
				draw.text(
					(text_x, text_y),
					text,
					font=font1,
					fill=(255,255,255)
				)
			card_index += 1



	background.save("user_cards.png")

	return background

async def give_card(user_id, card_id, card_name, quantity=1):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute(
				"""
				INSERT INTO user_cards (discord_id, card_id, name, quantity)
				VALUES (%s, %s, %s, %s)
				ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
				""",
				(user_id, card_id, card_name, quantity),
			)
		await db.commit()

rarities = [
		("common", 889),
		("epic", 100),
		("legendary", 10),
		("mythic", 1)
	]

card_pools = {
	"common": [
		"card_common_1",
		"card_common_2",
		"card_common_3",
		"card_common_4"
	],
	"epic": [
		"card_epic_1",
		"card_epic_2",
		"card_epic_3"
	],
	"legendary": [
		"card_legendary_1",
		"card_legendary_2"
	],
	"mythic": [
		"card_mythic_1"
	]
}
def random_card(cards):

	total = sum(weight for _, weight in rarities)
	r = random.randint(1, total)

	current = 0
	rarity = None

	for card, weight in rarities:
		current += weight
		if r <= current:
			rarity = card
			break

	return random.choice(card_pools[rarity])


async def change_boosterpack_amount(discord_id, amount: int = 1):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute(
				"""
				INSERT INTO korttipakat (discord_id, boosterpacks)
				VALUES (%s, %s)
				ON DUPLICATE KEY UPDATE
					boosterpacks = GREATEST(boosterpacks + VALUES(boosterpacks), 0)
				""",
				(discord_id, amount),
			)

		await db.commit()


async def get_number_of_boosterpacks(discord_id):
		async with get_db_connection() as db:
			async with db.cursor(aiomysql.DictCursor) as cursor:
				await cursor.execute(
					"""
					SELECT boosterpacks
					FROM korttipakat
					WHERE discord_id = %s;
					""",
					(discord_id,),
				)
				row = await cursor.fetchone()

				if row:
					return row["boosterpacks"]
				return 0;

def setup_buy_boosterpack(client):
	@client.slash_command(name = "osta_korttipakka", description = "Hinta: 50 niilopistettä", guild_ids=[SERVER_ID])
	async def korttipakkacom(interaction: disnake.ApplicationCommandInteraction):
		await interaction.response.defer()
		if await remove_points(client, interaction.author.id, 50):
			await change_boosterpack_amount(interaction.author.id, 1)
			korttipakat = await get_number_of_boosterpacks(interaction.author.id)
			if korttipakat == 1:
				await interaction.followup.send(f"Sulla on nyt {korttipakat} korttipakka.")
			else:
				await interaction.followup.send(f"Sulla on nyt {korttipakat} korttipakkaa.")
		else:
			await interaction.followup.send(f"https://tenor.com/view/niilo-niilo22-mene-toihin-mee-gif-8148789")



#Avaa korttipakka komento.
def setup_open_boosterpack(client):

	@client.slash_command(name = "avaa_korttipakka", description = "En oo syöny keksiä", guild_ids=[SERVER_ID])
	async def kortticom(interaction: disnake.ApplicationCommandInteraction):
		await interaction.response.defer()
		if await get_number_of_boosterpacks(interaction.author.id):
			await change_boosterpack_amount(interaction.author.id, -1)
			card_id = random_card(cards)
			card_name = next(name for cid, name in cards if cid == card_id)
			await give_card(interaction.author.id, card_id, card_name)

			image = card_mapping.get(f":{card_id}:")
			buffer = io.BytesIO()
			image.save(buffer, format="PNG")
			buffer.seek(0)
			file = disnake.File(buffer, filename="card.png")
			embed = disnake.Embed(description=f"Sait kortin: **{card_name}**")
			embed.set_image(url="attachment://card.png")

			await interaction.followup.send(embed=embed, file=file)
		else:
			await interaction.followup.send(f"Sulla ei oo korttipakkoja")