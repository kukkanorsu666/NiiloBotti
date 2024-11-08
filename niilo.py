import nextcord, os, random, scrapetube, datetime, time, requests, openai, asyncio, logging
from asyncio import sleep
from nextcord import FFmpegPCMAudio
from nextcord.ext import tasks, commands
from nextcord import Interaction
from nextcord import SlashOption
from typing import Optional
from pytube import extract
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup

intents = nextcord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
	print("Valmis")
	await daily_loop()

BOT_TOKEN = "BOT TOKEN"
SERVER_ID = "SERVER ID"
CHANNEL_ID = "CHANNEL ID"

openai.api_key = 'API_KEY'

script_dir = os.path.dirname(__file__)
relative_path_wav = "Sound/"
voice_path_wav = os.path.join(script_dir, relative_path_wav)

#SOCS 13 kk uus tarvittaessa
channel_url = "https://www.youtube.com/@niilo22games/"
content = requests.get(channel_url, cookies={"CONSENT":"PENDING+696969", "SOCS":"CAESEwgDEgk2OTA4MDQ2NDQaAmVuIAEaBgiAkYu5Bg"}).text
ENCODED = str(content).encode("ascii", "ignore")

logging.basicConfig(filename='errorlog.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
#RANDOM LUIKAUS
def luikaus():
	random_luikaus = open("luikaukset.txt", encoding='utf-8').read().splitlines()
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
	interaction: nextcord.Interaction,
	numero: Optional[int] = SlashOption(required=False)):

	if numero is None or numero > 195 or numero < 0:
		await interaction.response.send_message(luikaus())

	else:
		await interaction.response.send_message(valittuluikaus(numero))


#RANDOM VIDEOKOMENTO
@client.slash_command(name = "video", description = "Tästä videoustia", guild_ids=[SERVER_ID])
async def videocom(interaction: Interaction):
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
		voice = await channel.connect()
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

	if "katsojaa" in ENCODED.decode():
		channel1 = client.get_channel(CHANNEL_ID)
		await channel1.send("Rupeen tästä pelailemaan\nhttps://www.youtube.com/@niilo22games/live")
		await sleep(36000)


@tasks.loop(minutes=2)
async def live_status():
	await client.wait_until_ready()

	if "katsojaa" in ENCODED.decode():
		r = requests.get("https://www.youtube.com/@niilo22games/live")
		s = BeautifulSoup(r.text)
		link = s.find_all(name="title")[0]
		title = link.text
		title = title.replace(" - YouTube","")
		await client.change_presence(activity=nextcord.CustomActivity(name=f"Striimaa {title}"))
	else:
		await client.change_presence(activity=nextcord.CustomActivity(name="Hyvää joulun odotusta & lumen"))


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

	transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fi'])
	text = ""
	for x in transcript:
		text = text + " " + x["text"]

	text = text.replace('[Musiikkia]', '')
	text = text.replace('\n', '')

	completion = openai.chat.completions.create(
		model="gpt-4o",
		messages=[
			{"role": "user", "content": f"Vastauksessa tulee olla alle 1500 kirjainta. Videossa puhuu Niilo. Voitko listata lyhyesti suomeksi tästä videosta oleelliset asiat?: {text}"}
		],
	)

	print(completion.choices[0].message.content)

	ai_summary = completion.choices[0].message.content
	
	return ai_summary


@tasks.loop(minutes=1)
async def daily_loop():
	x = datetime.time(16, 0)
	schedule_time_hour = x.hour
	schedule_time_minute = x.minute

	if schedule_time_hour  == datetime.datetime.now().hour and schedule_time_minute == datetime.datetime.now().minute:
		channel = client.get_channel(CHANNEL_ID)
		try:
			await channel.send("_" + ai_summary()+ "_" + "\n" + daily())
		except openai.OpenAIError as err:
			await channel.send("_" + "Napsahti että pärähti! (joku meni pieleen)" + "_" + "\n" + daily())
			logger.error(err)
		

daily_loop.start()
live_check.start()
live_status.start()
client.run(BOT_TOKEN)
