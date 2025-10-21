import disnake, os, random, scrapetube, datetime, time, requests, openai, asyncio, aiomysql, json
from asyncio import sleep
from disnake.ext import tasks, commands
from disnake import Interaction, FFmpegPCMAudio
from typing import Optional
from pytube import extract
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
from contextlib import asynccontextmanager

intents = disnake.Intents.all()
intents.members = True
intents.messages = True
intents.message_content = True
intents.voice_states = True
intents.reactions = True
intents.guilds = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
	daily_loop.start()
	live_check.start()
	luikaus_loop.start()
	live_status.start()
	print("Valmis")

with open("config.json") as f:
	config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
SERVER_ID = int(config["SERVER_ID"])
CHANNEL_ID = int(config["CHANNEL_ID"])
openai.api_key = config["openai.api_key"]

script_dir = os.path.dirname(__file__)
relative_path_wav = "Sound/"
voice_path_wav = os.path.join(script_dir, relative_path_wav)


#Database
tracked_message_id = None


DB_CONFIG = {
  "host": config["host"],
  "user": config["user"],
  "password": config["password"],
  "db": config["database"],
  "autocommit": True
}

@asynccontextmanager
async def get_db_connection():
	db = await aiomysql.connect(**DB_CONFIG)
	try:
		yield db
	finally:
		db.close()

async def give_points_daily():
	print("giving daily poinsts...")
	async with get_db_connection() as db:
		async with db.cursor() as cursor:
			for guild in client.guilds:
				for member in guild.members:
					if member.bot:
						continue
											
					await cursor.execute("""
                        INSERT INTO niilopisteet (discord_id, points)
                        VALUES (%s, 1)
                        ON DUPLICATE KEY UPDATE points = points + VALUES(points)
                        """,
                        (member.id,)
                    )
			await db.commit()


async def give_points(discord_id, points):
		async with get_db_connection() as db:
			async with db.cursor() as cursor:
				sql = """
						INSERT INTO niilopisteet (discord_id, points)
						VALUES (%s, %s)
						ON DUPLICATE KEY UPDATE points = points + VALUES(points)
				"""
				values = (discord_id, points)
				await cursor.execute(sql, values)
			await db.commit()

async def fetch_points(discord_id: int):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("SELECT points FROM niilopisteet WHERE discord_id = %s", (discord_id,))
			row = await cursor.fetchone()
			return row["points"] if row else 0

async def remove_point(ctx, n: int):
	current = await fetch_points(n)

	if current <= 0:
			await ctx.send("https://tenor.com/view/niilo-niilo22-mene-toihin-mee-gif-8148789")
			return False

	async with get_db_connection() as db:
		async with db.cursor() as cursor:

						await cursor.execute(
								"""
								INSERT INTO niilopisteet (discord_id, points)
								VALUES (%s, 0)
								ON DUPLICATE KEY UPDATE points = points - 1
								""",
								(n,),
						)
		await db.commit()
	return True


@client.slash_command(name = "niilopisteet", description = "Näe niilopisteesi", guild_ids=[SERVER_ID])
async def pisteetcom(interaction: disnake.ApplicationCommandInteraction):
	user_id = interaction.user.id
	points = await fetch_points(user_id)
	await interaction.response.send_message(F"Sulla on {points} niilopistettä")


#RANDOM LUIKAUS
def luikaus():
	random_luikaus = open("luikaukset.txt", encoding='utf-8').read().splitlines()
	return random.choice(random_luikaus)

def gifu():
	random_luikaus = open("gifut.txt", encoding='utf-8').read().splitlines()
	return random.choice(random_luikaus)


#EI NIIN RANDOM LUIKAUS
def valittuluikaus(x):
	with open("luikaukset.txt", encoding='utf-8') as onh:
		arr = onh.readlines()
		return arr[x]


#RANDOM VIDEO
def video():
	random_video = open('videot.txt', encoding='utf-8').read().splitlines()
	return random.choice(random_video)


#LUIKAUSKOMENTO
@client.slash_command(name = "luikaus", description = "Ei siitä sen enempää", guild_ids=[SERVER_ID])
async def luikauscom(
	interaction: disnake.ApplicationCommandInteraction,
	numero: Optional[int] = None):

	if numero is None or numero > 195 or numero < 0:
		await interaction.response.send_message(luikaus())

	else:
		await interaction.response.send_message(valittuluikaus(numero))

#GIFUKOMENTO
@client.slash_command(name = "gifu", description = "Ei siitä sen enempää", guild_ids=[SERVER_ID])
async def gifucom(interaction: disnake.ApplicationCommandInteraction):
	await interaction.response.send_message(gifu())

#RANDOM VIDEOKOMENTO
@client.slash_command(name = "video", description = "Tästä videoustia", guild_ids=[SERVER_ID])
async def videocom(interaction: disnake.ApplicationCommandInteraction):
	await interaction.response.send_message((video()))


#RANDOM ÄÄNIKLIPPI
def random_voice():
	random_voice = random.choice(os.listdir(voice_path_wav))
	print("playing -- " + random_voice)
	return random_voice


#CONNECT VOICE
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


#LIVE CHECK
@tasks.loop(minutes=2)
async def live_check():
	await client.wait_until_ready()

	channel_url = "https://www.youtube.com/@niilo22games/"
	content = requests.get(channel_url, cookies={"CONSENT":"PENDING+696969", "SOCS":"CAESEwgDEgk2OTA4MDQ2NDQaAmVuIAEaBgiAkYu5Bg"}).text
	ENCODED = str(content).encode("ascii", "ignore")

	if "katsojaa" in ENCODED.decode():
		channel1 = client.get_channel(CHANNEL_ID)
		await channel1.send("Rupeen tästä pelailemaan\nhttps://www.youtube.com/@niilo22games/live")
		await sleep(36000)


@tasks.loop(minutes=2)
async def live_status():
	await client.wait_until_ready()

	channel_url = "https://www.youtube.com/@niilo22games/"
	content = requests.get(channel_url, cookies={"CONSENT":"PENDING+696969", "SOCS":"CAESEwgDEgk2OTA4MDQ2NDQaAmVuIAEaBgiAkYu5Bg"}).text
	ENCODED = str(content).encode("ascii", "ignore")

	if "katsojaa" in ENCODED.decode():
		r = requests.get("https://www.youtube.com/@niilo22games/live")
		s = BeautifulSoup(r.text, "html.parser")
		link = s.find_all(name="title")[0]
		title = link.text
		title = title.replace(" - YouTube","")
		await client.change_presence(activity=disnake.CustomActivity(name=f"Striimaa {title}"))
	else:
		await client.change_presence(activity=disnake.CustomActivity(name="asia on nyt tähän"))


#PÄIVÄN VIDEO
def daily():
	videos = scrapetube.get_channel("UC7WlCq3wvnxgBEbVA9Dyo9w")
	for video in videos:
		videoid = video['videoId']
		paivan_video = ("https://www.youtube.com/watch?v=" + videoid)
		return paivan_video


def ai_summary():
	url = daily()
	video_id = extract.video_id(url)

	transcript_obj = YouTubeTranscriptApi().fetch(video_id, languages=['fi'])
	text = ""
	fetched_transcript = transcript_obj.to_dict()
	text = " ".join([x["text"] for x in fetched_transcript])
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


@tasks.loop(minutes = 1)
async def luikaus_loop():
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


@tasks.loop(minutes=1)
async def daily_loop():
	x = datetime.time(16, 24)
	scheduled_time_hour = x.hour
	scheduled_time_minute = x.minute

	global tracked_message_id

	if scheduled_time_hour  == datetime.datetime.now().hour and scheduled_time_minute == datetime.datetime.now().minute:
		await give_points_daily()
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

#Reaktio bonari
handled_reactions = set()
@client.event
async def on_reaction_add(reaction, user):
	global handled_reactions

	if user == client.user:
		return

	if reaction.message.id == tracked_message_id and reaction.message.id not in handled_reactions:
		handled_reactions.add(reaction.message.id)
		await reaction.message.channel.send(f"{user.mention} ansaitsi 5 niilopistettä")
		await give_points(user.id, 5)

client.run(BOT_TOKEN)
