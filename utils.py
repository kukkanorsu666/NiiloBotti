from imports import *
from config import *
from db import *

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


#RANDOM ÄÄNIKLIPPI
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


#Lotto skripti/gifin valmistus
async def lotto(client, interaction, mention, discord_id, panos):
	selected_gifs, jackpot, mid_win, low_win = await pick_gifs()
	def make_gif():
		clips = [VideoFileClip(p) for p in selected_gifs]
		max_duration = max(c.duration for c in clips)
		processed_clips = []
		bg_color = (255, 255, 255)

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
		final_clip = clips_array([processed_clips]).with_fps(8)
		final_clip.write_gif("lotto.gif", fps=8, loop=None)

	await asyncio.to_thread(make_gif)
	channel = client.get_channel(CHANNEL_ID)
	await interaction.followup.send(f"Pyöräyttäjä: {mention} panoksella: {panos} ", file=disnake.File("lotto.gif"))

	await asyncio.sleep(10)
	if jackpot:
		
		await interaction.followup.send(f"{mention} sai JÄKPOTIN ja voitti {panos * 12} niilopistettä!")
		await give_points(discord_id, panos * 12)
	elif mid_win:
		await interaction.followup.send(f"{mention} sai 3 peräkkäin ja voitti {panos * 4} niilopistettä!")
		await give_points(discord_id, panos * 4)
	elif low_win:
		await interaction.followup.send(f"{mention} sai 2 peräkkäin ja voitti omat takas")
		await give_points(discord_id, panos * 1)
	else:
		await interaction.followup.send("Parempi tuuri ens kerralla")

#Panoksen maksu
async def pay_bet(client, discord_id: int, bet: int):
	current = await fetch_points(discord_id)
	channel = client.get_channel(CHANNEL_ID)

	if current <= 0:
			await channel.send("https://tenor.com/view/niilo-niilo22-mene-toihin-mee-gif-8148789")
			return
	else:

		async with get_db_connection() as db:
			async with db.cursor() as cursor:

				await cursor.execute(
								"""
								INSERT INTO niilopisteet (discord_id, points)
								VALUES (%s, 0)
								ON DUPLICATE KEY UPDATE points = GREATEST(points - %s, 0)
								""",
								(discord_id, bet),
						)
			await db.commit()
		return