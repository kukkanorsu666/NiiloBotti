import nextcord, os, random, scrapetube, datetime, time
from asyncio import sleep
from nextcord import FFmpegPCMAudio
from nextcord.ext import tasks, commands
from nextcord import Interaction

intents = nextcord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
	await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="Bengalin tiikeri"))
	print("Valmis")
	await daily_loop()


SERVER_ID = SERVER ID HERE
CHANNEL_ID = CHANNEL ID HERE


#RANDOM LUIKAUS
def luikaus(luikaukset):
    random_luikaus = open("luikaukset.txt", encoding='utf-8').read().splitlines()
    return random.choice(random_luikaus)

#RANDOM VIDEO
def video(videot):
    random_video = open('videot.txt', encoding='utf-8').read().splitlines()
    return random.choice(random_video)

#LUIKAUSKOMENTO
@client.slash_command(name = "luikaus", description = "Ei siitä sen enempää", guild_ids=[SERVER_ID])
async def testcommand(interaction: Interaction):
	await interaction.response.send_message(luikaus(luikaus))

#RANDOM VIDEOKOMENTO
@client.slash_command(name = "video", description = "Tästä videoustia", guild_ids=[SERVER_ID])
async def testcommand(interaction: Interaction):
	await interaction.response.send_message((video(video)))

#RANDOM ÄÄNIKLIPPI
def random_voice(voice_):
	random_voice = open('voice.txt', encoding='utf-8').read().splitlines()
	return random.choice(random_voice)
	
#CONNECT VOICE
@client.command(pass_context = True)
async def n(ctx):
	if(ctx.author.voice):
		channel = ctx.message.author.voice.channel
		voice = await channel.connect()
		chosen_voice = random_voice(random_voice)
		print(chosen_voice)
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


#PÄIVÄN VIDEO
def daily():
	videos = scrapetube.get_channel("UC7WlCq3wvnxgBEbVA9Dyo9w")
	for video in videos:
		videoid = video['videoId']
		paivan_video = ("https://www.youtube.com/watch?v=" + videoid)
		return paivan_video

@tasks.loop(minutes=1)
async def daily_loop():
	x = datetime.time(16, 0)
	schedule_time_hour = x.hour
	schedule_time_minute = x.minute


	if schedule_time_hour  == datetime.datetime.now().hour and schedule_time_minute == datetime.datetime.now().minute:
		channel = client.get_channel(CHANNEL ID HERE)
		await channel.send(daily())


client.run(PRIVATE KEY HERE)
daily_loop.start()
