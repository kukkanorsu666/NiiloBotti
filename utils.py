from imports import *
from config import *
from db import give_points, get_db_connection, fetch_points
from PIL import Image, ImageFont, ImageDraw
import re

#Valitsee satunnaisen luikauksen luikaukset.txt tiedostosta
def luikaus():
	random_luikaus = open("luikaukset.txt", encoding='utf-8').read().splitlines()
	return random.choice(random_luikaus)

#Valitsee satunnaisen gifin gif kansiosta
def gifu():
	random_gifu = open("gifut.txt", encoding='utf-8').read().splitlines()
	return random.choice(random_gifu)


#Käyttäjä voi itse valita haluamansa luikauksen
def valittuluikaus(x):
	with open("luikaukset.txt", encoding='utf-8') as onh:
		arr = onh.readlines()
		return arr[x]


#Valitsee satunnaisen luikauksen
def video():
	random_video = open('videot.txt', encoding='utf-8').read().splitlines()
	return random.choice(random_video)



def ai_summary():
	url = daily()
	video_id = extract.video_id(url)

	transcript = YouTubeTranscriptApi().fetch(video_id, languages=['fi'])
	
	text = " ".join([snippet.text for snippet in transcript])
	text = text.replace("[Musiikkia]", "").replace("\n", "")

	completion = openai.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "user", "content": f"Vastauksessa tulee olla alle 300 kirjainta. Videossa puhuu Niilo. Voitko listata lyhyesti suomeksi tästä videosta oleelliset asiat?: {text}"}
		],
	)

	print(completion.choices[0].message.content)

	ai_summary = completion.choices[0].message.content
	
	return ai_summary


#Valitaan satunnainen ääni
def random_voice():
	random_voice = random.choice(os.listdir(voice_path_wav))
	print("playing -- " + random_voice)
	return random_voice


#Valitaan gifit hedelmäpeliin ja tarkistetaan voitto
async def pick_gifs():
	columns = 4
	selected_gifs = []
	results = []

	for i in range(1, columns + 1):
		r = random.choice([0, 1])
		results.append(r)
		if r == 1:
			selected_gifs.append(os.path.join(gif_folder_path, f"v{i}.gif"))
		else:
			selected_gifs.append(os.path.join(gif_folder_path, f"h{i}.gif"))

	pattern = "".join(map(str, results))
	jackpot = pattern == "1111"
	mid_win = "111" in pattern and not jackpot
	low_win = "11" in pattern and not mid_win and not jackpot

	return selected_gifs, jackpot, mid_win, low_win


#Hakee uusimman videon Niilon kanavalta
def daily():
	videos = scrapetube.get_channel("UC7WlCq3wvnxgBEbVA9Dyo9w")
	for video in videos:
		videoid = video['videoId']
		paivan_video = ("https://www.youtube.com/watch?v=" + videoid)
		return paivan_video

async def get_total_bet(discord_id: int):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("SELECT SUM(bet_amount) AS total FROM gamble_history WHERE discord_id=%s", (discord_id,))
			row = await cursor.fetchone()
			return row['total'] if row['total'] else 0

#Lotto skripti/gifin valmistus
async def lotto(client, interaction, mention, discord_id, panos):
	selected_gifs, jackpot, mid_win, low_win = await pick_gifs()
	def make_gif():
		clips = [VideoFileClip(p) for p in selected_gifs]
		max_duration = max(c.duration for c in clips)
		processed_clips = []
		bg_color = (255,255,255)

		for c in clips:
			if c.duration < max_duration:
				last_frame_array = c.get_frame(c.duration - 1 / c.fps)
				last_frame_clip = ImageClip(last_frame_array).with_duration(max_duration - c.duration)
				c_final = concatenate_videoclips([c, last_frame_clip])
			else:
				c_final = c

			solid_bg = ColorClip(size=c_final.size, color=bg_color).with_duration(max_duration)
			c_final = CompositeVideoClip([solid_bg, c_final])
			processed_clips.append(c_final)

		min_height = min(c.h for c in processed_clips)
		processed_clips = [c.resized(height=min_height) for c in processed_clips]
		final_clip = clips_array([processed_clips]).with_fps(12)
		final_clip.write_gif("lotto.gif", fps=12, loop=None)

	await asyncio.to_thread(make_gif)
	channel = client.get_channel(CHANNEL_ID)
	await interaction.followup.send(f"Pyöräyttäjä: {mention} panoksella: {panos} ", file=disnake.File("lotto.gif"))

	await asyncio.sleep(10)
	if jackpot:
		await interaction.followup.send(f"{mention} sai JÄKPOTIN ja voitti {panos * 12} niilopistettä!")
		await give_points(client, discord_id, panos * 12)
		result_amount = panos * 12
	elif mid_win:
		await interaction.followup.send(f"{mention} sai 3 peräkkäin ja voitti {panos * 4} niilopistettä!")
		await give_points(client, discord_id, panos * 4)
		result_amount = panos * 4
	elif low_win:
		await interaction.followup.send(f"{mention} sai 2 peräkkäin ja voitti omat takas")
		await give_points(client, discord_id, panos * 1)
		result_amount = panos * 1
	else:
		await interaction.followup.send("Parempi tuuri ens kerralla")
		result_amount = 0

	await check_achievements(client, discord_id, 'gamble_single_1000', panos)

	await check_achievements(client, discord_id, 'gamble_single_1000', panos)
	await check_achievements(client, discord_id, 'gamble_single_10000', panos)
	await check_achievements(client, discord_id, 'gamble_single_100000', panos)
	lose_streak_before = await get_lose_streak(discord_id)
	previous_total = await get_total_bet(discord_id)
	new_total = previous_total + panos
	await check_achievements(client,discord_id, 'gamble_total_1000', new_total)
	await check_achievements(client,discord_id, 'gamble_total_10000', new_total)
	await check_achievements(client,discord_id, 'gamble_total_100000', new_total)
	await log_gamble(discord_id, panos, result_amount)
	if result_amount == 0:
		lose_streak_after = lose_streak_before + 1
		await check_achievements(client, discord_id, 'gamble_lose_4', lose_streak_after)
	else:
		await check_achievements(client, discord_id, 'gamble_lose_4', 0)

async def get_lose_streak(discord_id: int) -> int:
	conn = await aiomysql.connect(**DB_CONFIG)
	async with conn.cursor() as cursor:
		await cursor.execute("""
			SELECT outcome
			FROM gamble_history
			WHERE discord_id = %s
			ORDER BY created_at DESC
			LIMIT 4
		""", (discord_id,))
        
		rows = await cursor.fetchall()

		streak = 0
		for r in rows:
			if r[0] == "lose":
				streak += 1
			else:
				break
		return streak

#Panoksen maksu
async def pay_bet(client, discord_id: int, bet: int):
	current = await fetch_points(discord_id)
    
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute(
				"""
				INSERT INTO niilopisteet (discord_id, points)
				VALUES (%s, 0)
				ON DUPLICATE KEY UPDATE points = GREATEST(points - %s, 0)
				""",
				(discord_id, bet),
			)

			await cursor.execute(
				"""
				UPDATE user_achievements
				SET progress = GREATEST(progress - %s, 0)
				WHERE discord_id = %s
					AND achievement_id IN (
						"points_total_1000",
						"points_total_10000",
						"points_total_100000",
						"points_total_1000000"
					)
				""",
					(bet, discord_id),
				)
			await cursor.execute(
				"""
				INSERT INTO user_achievements (discord_id, achievement_id, progress)
				VALUES (%s, 'gamble_count_300', 1)
				ON DUPLICATE KEY UPDATE progress = progress + 1
				""",
					(discord_id,),
				)

			await cursor.execute(
				"""
				SELECT progress
				FROM user_achievements
				WHERE discord_id = %s
					AND achievement_id = 'gamble_count_300'
				""",
					(discord_id,),
				)
			data = await cursor.fetchone()
		await db.commit()


	gamble_count = data["progress"]
	new_points = await fetch_points(discord_id)
	await check_achievements(client, discord_id, 'gamble_count_300', gamble_count)
	await check_achievements(client, discord_id, 'points_total_1000', new_points)
	await check_achievements(client, discord_id, 'points_total_10000', new_points)
	await check_achievements(client, discord_id, 'points_total_100000', new_points)
	await check_achievements(client, discord_id, 'points_total_1000000', new_points)

	if new_points <= 0:
		channel = client.get_channel(CHANNEL_ID)
		await channel.send("https://tenor.com/view/niilo-niilo22-mene-toihin-mee-gif-8148789")
		await check_achievements(client, discord_id, 'points_total_0', 1)

	return

#Tekstien ja taustan käsittely
def draw_text_with_rounded_bg(draw, background, text, font, emoji_mapping, x, y, bg_color=(0,0,0,0), text_color=(255,255,255), radius=10, padding=10, line_spacing=4, last_line_font=None):
	shortcode_pattern = re.compile(r'(:\w+:)')

	lines = text.split("\n")
	line_sizes = []

	for i, line in enumerate(lines):
		current_font = last_line_font if (last_line_font and i == len(lines)-1) else font
		total_width = 0
		max_height = 0
		parts = shortcode_pattern.split(line)
		combined = []

		for part in parts:
			if part in emoji_mapping:
				emoji_img = emoji_mapping[part]
				w, h = emoji_img.size
				combined.append((part, "emoji", w, h))
			else:
				bbox = draw.textbbox((0,0), part, font=current_font)
				w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
				combined.append((part, current_font, w, h))
			total_width += w
			max_height = max(max_height, h)
		line_sizes.append((total_width, max_height, combined))

	max_width = max(w for w, h, c in line_sizes)
	total_height = sum(h for w, h, c in line_sizes) + line_spacing * (len(lines)-1)

	overlay = Image.new("RGBA", (max_width + 2*padding, total_height + 2*padding), (0,0,0,0))
	overlay_draw = ImageDraw.Draw(overlay)

	overlay_draw.rounded_rectangle(
		(0, 0, max_width + 2*padding, total_height + 2*padding),
		radius=radius,
		fill=bg_color
	)

	current_y = padding
	for total_w, h, combined in line_sizes:
		current_x = padding
		corrected_y = current_y
		for part, f, w, ph in combined:
			if f == "emoji":
				emoji_img = emoji_mapping[part].convert("RGBA")
				emoji_y = corrected_y + (h - ph) // 2
				overlay.paste(emoji_img, (int(current_x), int(emoji_y)), emoji_img)
			else:
				overlay_draw.text((current_x, corrected_y), part, font=f, fill=text_color)
			current_x += w
		current_y += h + line_spacing

	background.alpha_composite(overlay, (x - padding, y - padding))

achievements_to_check = [
	("all_achievements", "Saavutusten hamstraaja", "Ansaitse kaikki saavutukset."),
	("gamble_count_300", "Uhkapelihullu", "Pelaa lottoa 300 kertaa."),
	("gamble_lose_4", "Putki Epätuuria", "Häviä 4 peliä putkeen."),
	("gamble_single_1000", "Yksi Paniikki", "Pelaa 1000 pistettä yhdellä kerralla."),
	("gamble_single_10000", "Hurja Heittäjä", "Pelaa 10000 pistettä yhdellä kerralla."),
	("gamble_single_100000", "Täysriski", "Pelaa 100000 pistettä yhdellä kerralla."),
	("gamble_total_1000", "Ensimmäinen Panos", "Pelaa 1000 pistettä yhteensä."),
	("gamble_total_10000", "Pelikoneen Kaveri", "Pelaa 10000 pistettä yhteensä."),
	("gamble_total_100000", "Iso Kalastaja", "Pelaa 100000 pistettä yhteensä."),
	("gamble_with_0", "Rohkea Sisu", "Yritä pelata 0 panoksella."),
	("points_total_0", "Tyhjä Tasku", "Tyhjennä pistetili."),
	("points_total_1000", "Nousija", "Kerää 1000 pistettä."),
	("points_total_10000", "Taituri", "Kerää 10000 pistettä."),
	("points_total_100000", "Suuruudenhullu", "Kerää 100000 pistettä."),
	("points_total_1000000", "Pistemiljonääri", "Kerää miljoona pistettä."),
	("reaction_streak_3", "Kolmen Päivän Kuuma", "Reagoi päivän videoon kolmena peräkkäisenä päivänä."),
	("reaction_streak_7", "Viikon Velho", "Reagoi päivän videoon seitsemänä peräkkäisenä päivänä."),
	("reaction_wins_10", "Nopea Kättä", "Reagoi kymmenen kertaa päivän videoon."),
	("reaction_wins_30", "Salamannopea", "Reagoi 30 kertaa päivän videoon."),
	("reaction_wins_50", "Refleksimestari", "Reagoi 50 kertaa päivän videoon."),
	]

async def get_achievement_emojis(discord_id):

	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			achievement_emojis = {}
			for achievement_id, _, _ in achievements_to_check:
				await cursor.execute("""
					SELECT unlocked
					FROM user_achievements
					WHERE discord_id=%s AND achievement_id=%s
				""", (discord_id, achievement_id))
				row = await cursor.fetchone()
				achievement_emojis[achievement_id] = ":checkmark:" if row and row['unlocked'] == 1 else ":x:"
			return achievement_emojis

async def get_user_achievement_progress(discord_id):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			achievement_data = {}
			for achievement_id, _, _ in achievements_to_check:
				await cursor.execute("""
					SELECT progress, unlocked
					FROM user_achievements
					WHERE discord_id=%s AND achievement_id=%s
				""", (discord_id, achievement_id))
				row = await cursor.fetchone()
				progress = row['progress'] if row else 0
				unlocked = row['unlocked'] == 1 if row else False
				emoji = ":checkmark:" if unlocked else ":x:"
				achievement_data[achievement_id] = {"emoji": emoji, "progress": progress, "unlocked": unlocked}
			return achievement_data

#Saavutusten näyttäminen
async def show_achievements(client,discord_id, user):
	emoji_mapping = {
	":checkmark:": Image.open("emojis/checkmark.png").resize((50,50)),
	":x:": Image.open("emojis/x.png").resize((50,50)),
	":rank_1:": Image.open("emojis/level-1.png").resize((50,50)),
	":rank_2:": Image.open("emojis/level-2.png").resize((50,50)),
	":rank_3:": Image.open("emojis/level-3.png").resize((50,50)),
	":rank_4:": Image.open("emojis/level-4.png").resize((50,50)),
	":rank_5:": Image.open("emojis/level-5.png").resize((50,50)),
	":rank_6:": Image.open("emojis/level-6.png").resize((50,50)),
	":rank_7:": Image.open("emojis/level-7.png").resize((50,50)),
	":rank_8:": Image.open("emojis/crown.png").resize((50,50))
}
	width = 1400
	height = 1600
	background = Image.new("RGBA", (width, height), (0,0,0,0))

	font1 = ImageFont.truetype("fonts/Play-Bold.ttf", 30)
	font2 = ImageFont.truetype("fonts/Play-Regular.ttf", 24)
	font3 = ImageFont.truetype("fonts/Play-Bold.ttf", 60)
	font4 = ImageFont.truetype("fonts/Play-Regular.ttf", 45)
	achievement_emojis = await get_achievement_emojis(user.id)

	mid_index = len(achievements_to_check) // 2
	left_achievements = achievements_to_check[:mid_index]
	right_achievements = achievements_to_check[mid_index:]

	left_x = 100
	right_x = 700
	left_y = 230
	right_y = 230
	spacing = 120

	achievement_progress = await get_user_achievement_progress(user.id)
	


	for achievement_id, name, description in left_achievements:
		unlocked = achievement_progress[achievement_id]["unlocked"]
		emoji = achievement_emojis.get(achievement_id, ":x:")

		async with get_db_connection() as db:
			async with db.cursor(aiomysql.DictCursor) as cursor:
				await cursor.execute(
					"SELECT requirement_value FROM achievements WHERE achievement_id=%s",
					(achievement_id,)
			)
			required = (await cursor.fetchone())['requirement_value']
			progress = achievement_progress[achievement_id]["progress"]

		text_to_draw = f"{emoji} {name} ({progress}/{required})\n{description}"
		draw_text_with_rounded_bg(
			draw=ImageDraw.Draw(background),
			background=background,
			text=text_to_draw,
			font=font1,
			emoji_mapping=emoji_mapping,
			last_line_font=font2,
			x=left_x,
			y=left_y,
			bg_color=(0, 120, 200, 0),
			text_color=(255, 255, 255),
			radius=12,
			padding=12,
			line_spacing=4
		)
		left_y += spacing

	for achievement_id, name, description in right_achievements:
		unlocked = achievement_progress[achievement_id]["unlocked"]
		emoji = achievement_emojis.get(achievement_id, ":x:")


		async with get_db_connection() as db:
			async with db.cursor(aiomysql.DictCursor) as cursor:
				await cursor.execute(
					"SELECT requirement_value FROM achievements WHERE achievement_id=%s",
					(achievement_id,)
			)
			required = (await cursor.fetchone())['requirement_value']
			progress = achievement_progress[achievement_id]["progress"]

		text_to_draw = f"{emoji} {name} ({progress}/{required})\n{description}"
		draw_text_with_rounded_bg(
			draw=ImageDraw.Draw(background),
			background=background,
			text=text_to_draw,
			font=font1,
			emoji_mapping=emoji_mapping,
			last_line_font=font2,
			x=right_x,
			y=right_y,
			bg_color=(0, 120, 200, 0),
			text_color=(255, 255, 255),
			radius=12,
			padding=12,
			line_spacing=4
		)
		right_y += spacing

	#Käyttäjän profiilikuva
	user_picture = user.display_avatar.url
	img_data = requests.get(user_picture).content
	with open('user_image.png', 'wb') as handler:
		handler.write(img_data)
	user_image = Image.open("user_image.png").convert("RGBA")
	user_image = user_image.resize((100,100))
	#Käyttäjän nimi
	user_name = user.name
	user_display_mame = user.display_name
	color = user.color.to_rgb()
	ImageDraw.Draw(background).text((220, 85),f"{user_display_mame}",(color),font=font3)
	ImageDraw.Draw(background).text((220, 150),f"{user_name}",(color),font=font4)

	background.paste(user_image, (100, 100), user_image)
	background.save("user_achievements.png")


	return background


############################SAAVUTUKSET############################

#Tallennetaan pelihistoria tietokantaan
async def log_gamble(discord_id: int, bet_amount: int, result_amount: int):
	outcome = 'win' if result_amount > 0 else 'lose'
	conn = await aiomysql.connect(**DB_CONFIG)

	async with conn.cursor() as cursor:

		await cursor.execute("SELECT COALESCE(MAX(total_bet), 0) FROM gamble_history WHERE discord_id = %s", (discord_id,))
		last_total = await cursor.fetchone()
		last_total_bet = last_total[0] if last_total else 0

		new_total_bet = last_total_bet + bet_amount

		await cursor.execute("""
			INSERT INTO gamble_history (discord_id, bet_amount, result_amount, outcome, created_at, total_bet)
			VALUES (%s, %s, %s, %s, %s, %s)
		""", (discord_id, bet_amount, result_amount, outcome, datetime.datetime.now(), new_total_bet))

		await conn.commit()
	conn.close()

#Tarkistetaan saavutukset
async def check_achievements(client, discord_id: int, achievement_id: str, current_value: int):

	conn = await aiomysql.connect(**DB_CONFIG)
	async with conn.cursor(aiomysql.DictCursor) as cursor:
		#Haetaan saavutusten vaatimukset tietokannasta
		await cursor.execute("SELECT requirement_value, name FROM achievements WHERE achievement_id=%s", (achievement_id,))
		achievement = await cursor.fetchone()
		if not achievement:
			return

		required = achievement['requirement_value']
		achievement_name = achievement['name']

		#Haetaan käyttäjän edistys
		await cursor.execute("""
			SELECT unlocked, progress
			FROM user_achievements
			WHERE discord_id=%s AND achievement_id=%s
		""", (discord_id, achievement_id))
		row = await cursor.fetchone()
		unlocked_now = False

		if row is None:
			if current_value >= required:
				await cursor.execute("""
					INSERT INTO user_achievements (discord_id, achievement_id, progress, unlocked, unlocked_at)
					VALUES (%s, %s, %s, 1, %s)
				""", (discord_id, achievement_id, current_value, datetime.datetime.now()))
				unlocked_now = True
			else:
				await cursor.execute("""
					INSERT INTO user_achievements (discord_id, achievement_id, progress, unlocked)
					VALUES (%s, %s, %s, 0)
				""", (discord_id, achievement_id, current_value))

		else:
			already_unlocked = row["unlocked"] == 1

			if current_value >= required and not already_unlocked:
				await cursor.execute("""
					UPDATE user_achievements
					SET unlocked = 1, progress = %s, unlocked_at = %s
					WHERE discord_id = %s AND achievement_id = %s
				""", (current_value, datetime.datetime.now(), discord_id, achievement_id))
				unlocked_now = True

			else:
				await cursor.execute("""
					UPDATE user_achievements
					SET progress = %s
					WHERE discord_id = %s AND achievement_id = %s
				""", (current_value, discord_id, achievement_id))
		await conn.commit()
	conn.close()

	if unlocked_now:
		channel = client.get_channel(CHANNEL_ID)
		await channel.send(f"<@{discord_id}> Ansaitsi saavutuksen: **{achievement_name}**!")
	await check_all_achievements_unlocked(client, discord_id)


async def get_total_reactions(discord_id: int) -> int:
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute(
				"SELECT reaction_count FROM user_reactions WHERE discord_id = %s",
				(discord_id,)
			)
			row = await cursor.fetchone()
			return row["reaction_count"] if row else 0

async def add_reaction(discord_id: int, amount: int = 1):
	async with get_db_connection() as db:
		async with db.cursor() as cursor:
			await cursor.execute("""
				INSERT INTO user_reactions (discord_id, reaction_count)
				VALUES (%s, %s)
				ON DUPLICATE KEY UPDATE reaction_count = reaction_count + VALUES(reaction_count)
			""", (discord_id, amount))
		await db.commit()


async def get_reaction_data(discord_id: int):
    async with get_db_connection() as db:
        async with db.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT reaction_count, last_reacted_at, reaction_streak
                FROM user_reactions
                WHERE discord_id=%s
            """, (discord_id,))
            return await cursor.fetchone()


async def update_reaction_data(discord_id: int, reaction_count: int, streak: int, now: datetime.datetime):
	async with get_db_connection() as db:
		async with db.cursor() as cursor:
			await cursor.execute("""
				UPDATE user_reactions
				SET reaction_count=%s,
					reaction_streak=%s,
					last_reacted_at=%s
				WHERE discord_id=%s
			""", (reaction_count, streak, now, discord_id))
		await db.commit()


async def update_reaction_streak_logic(discord_id: int, last_reactor_id: int) -> int:
	now = datetime.datetime.now()
	#Viimeisin reaktio
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("""
				SELECT discord_id, last_reacted_at
				FROM user_reactions
				WHERE last_reacted_at = (SELECT MAX(last_reacted_at) FROM user_reactions)
				ORDER BY discord_id, last_reacted_at
			""", )
			data1 = await cursor.fetchone()
		await db.commit()

	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("""
				SELECT reaction_count, last_reacted_at, last_reactor_id, reaction_streak
				FROM user_reactions
				WHERE discord_id=%s
			""", (discord_id,))
			data = await cursor.fetchone()

			if data is None:
				await cursor.execute("""
					INSERT INTO user_reactions (discord_id, reaction_count, last_reacted_at, reaction_streak, last_reactor_id)
					VALUES (%s, 1, %s, 1, %s)
				""", (discord_id, now, last_reactor_id))
				streak = 1
			else:
				old_streak = data["reaction_streak"]
				reaction_count = data["reaction_count"]
				if data1 is None:
					last_reactor = None
				else:
					last_reactor = data1.get("discord_id")
				print(last_reactor)

				if last_reactor != last_reactor_id:
					streak = 1
				else:
					streak = old_streak + 1

				await cursor.execute("""
					UPDATE user_reactions
					SET reaction_count = %s,
						reaction_streak = %s,
						last_reacted_at = %s,
						last_reactor_id = %s
					WHERE discord_id = %s
				""", (reaction_count, streak, now, last_reactor_id, discord_id))

		await db.commit()

	async with get_db_connection() as db:
		async with db.cursor() as cursor:
			for ach_id in ["reaction_streak_3", "reaction_streak_7"]:
				await cursor.execute("""
					INSERT INTO user_achievements (discord_id, achievement_id, progress, unlocked)
					VALUES (%s, %s, %s, 0)
					ON DUPLICATE KEY UPDATE progress = VALUES(progress)
				""", (discord_id, ach_id, streak))
		await db.commit()

	return streak


async def check_all_achievements_unlocked(client, discord_id: int):
    conn = await aiomysql.connect(**DB_CONFIG)
    async with conn.cursor(aiomysql.DictCursor) as cursor:

        await cursor.execute("""
            SELECT COUNT(*) AS total_count
            FROM achievements
            WHERE achievement_id != %s
        """, ('all_achievements',))
        total_achievements = (await cursor.fetchone())['total_count']

        await cursor.execute("""
            SELECT COUNT(*) AS unlocked_count
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.achievement_id
            WHERE ua.discord_id = %s AND ua.unlocked = 1 AND ua.achievement_id != %s
        """, (discord_id, 'all_achievements'))
        user_unlocked = (await cursor.fetchone())['unlocked_count']

        unlocked_now = False

        if user_unlocked == total_achievements:
            await cursor.execute("""
                SELECT unlocked
                FROM user_achievements
                WHERE discord_id = %s AND achievement_id = %s
            """, (discord_id, 'all_achievements'))
            row = await cursor.fetchone()

            if row is None:
                await cursor.execute("""
                    INSERT INTO user_achievements (discord_id, achievement_id, progress, unlocked, unlocked_at)
                    VALUES (%s, %s, %s, 1, %s)
                """, (discord_id, 'all_achievements', 1, datetime.datetime.now()))
                unlocked_now = True
            elif row['unlocked'] == 0:
                await cursor.execute("""
                    UPDATE user_achievements
                    SET unlocked = 1, progress = %s, unlocked_at = %s
                    WHERE discord_id = %s AND achievement_id = %s
                """, (1, datetime.datetime.now(), discord_id, 'all_achievements'))
                unlocked_now = True

        await conn.commit()
    conn.close()

    if unlocked_now:
        channel = client.get_channel(CHANNEL_ID)

        await channel.send(f"<@{discord_id}> Ansaitsi saavutuksen: **Saavutusten hamstraaja**!")
