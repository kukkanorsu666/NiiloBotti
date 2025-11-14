from imports import *
from config import CHANNEL_ID

#TODO
#Yhdistä funktiot

def setup_live_tasks(client):
	#Tarkistetaan onko Niilo live tilassa
	@tasks.loop(minutes=2)
	async def live_check():
		await client.wait_until_ready()

		channel_url = "https://www.youtube.com/@niilo22games/"
		content = requests.get(channel_url, cookies={"CONSENT":"PENDING+696969", "SOCS":"CAESEwgDEgk2OTA4MDQ2NDQaAmVuIAEaBgiAkYu5Bg"}).text
		ENCODED = str(content).encode("ascii", "ignore")

		if "katsojaa" in ENCODED.decode():
			channel = client.get_channel(CHANNEL_ID)
			await channel.send("Rupeen tästä pelailemaan\nhttps://www.youtube.com/@niilo22games/live")
			await sleep(36000)

	#Vaihdetaan botin status
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


	@live_check.before_loop
	async def before_live_check():
		await client.wait_until_ready()

	@live_status.before_loop
	async def before_live_status():
		await client.wait_until_ready()

	live_check.start()
	live_status.start()