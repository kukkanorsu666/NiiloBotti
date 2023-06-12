import nextcord
import os, random, asyncio, scrapetube, datetime, time, schedule, time
from asyncio import sleep
from nextcord import FFmpegPCMAudio
from nextcord.ext import tasks, commands
from nextcord import Interaction
from threading import Thread

intents = nextcord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
	await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="Bengalin tiikeri"))
	print("Valmis")
	await daily_loop()
	

SERVER_ID = 174153633770766336 #1048767466995732521
CHANNEL_ID = 174153633770766336 #1048767467633254512


#RANDOM LUIKAUS
def luikaus(luikaukset):
    random_luikaus = open("luikaukset.txt", encoding='utf-8').read().splitlines()
    return random.choice(random_luikaus)


#RANDOM VIDEO
def video(videot):
    random_video = open('videot.txt', encoding='utf-8').read().splitlines()
    return random.choice(random_video)
#print(video(video))


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
		#await ctx.guild.voice_client.disconnect()
			
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
		break

@tasks.loop(seconds=31)
async def daily_loop():
	x = datetime.time(16, 0)
	schedule_time_hour = x.hour
	schedule_time_minute = x.minute


	if schedule_time_hour  == datetime.datetime.now().hour and schedule_time_minute == datetime.datetime.now().minute:
		channel = client.get_channel(174153633770766336)
		await channel.send(daily())




client.run('MTAwNjExNzEyODY4MTgzMjUxOA.GJoLj4.CeN_v-_W8LqicOvtAK4u7azcMG5Ji0aDuK3T1Y')
daily_loop.start()