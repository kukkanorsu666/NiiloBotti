from imports import *
from config import DB_CONFIG


@asynccontextmanager
async def get_db_connection():
	db = await aiomysql.connect(**DB_CONFIG)
	try:
		yield db
	finally:
		db.close()
		
#Päivittäiset niilopisteet jaetaan päivän videon yhteydessä
async def give_points_daily(client):
	print("giving daily poinsts...")
	async with get_db_connection() as db:
		async with db.cursor() as cursor:
			for guild in client.guilds:
				for member in guild.members:
					if member.bot:
						continue
					discord_id = member.id
											
					await cursor.execute("""
                        INSERT INTO niilopisteet (discord_id, points)
                        VALUES (%s, 1)
                        ON DUPLICATE KEY UPDATE points = points + VALUES(points)
                        """,
                        (member.id,)
                    )
			await db.commit()
	for guild in client.guilds:
		for member in guild.members:
			if member.bot:
				continue
			discord_id = member.id
			current_points = await fetch_points(discord_id)

			from utils import check_achievements
			await check_achievements(client, discord_id, 'points_total_1000', current_points)
			await check_achievements(client, discord_id, 'points_total_10000', current_points)
			await check_achievements(client, discord_id, 'points_total_100000', current_points)
			await check_achievements(client, discord_id, 'points_total_1000000', current_points)

#Lisätään niilopisteitä
async def give_points(client, discord_id, points):
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

	current_points = await fetch_points(discord_id)
	from utils import check_achievements
	await check_achievements(client, discord_id, 'points_total_1000', current_points)
	await check_achievements(client, discord_id, 'points_total_10000', current_points)
	await check_achievements(client, discord_id, 'points_total_100000', current_points)
	await check_achievements(client, discord_id, 'points_total_1000000', current_points)

#Haetaan niilopisteet tietokannasta
async def fetch_points(discord_id: int):
	async with get_db_connection() as db:
		async with db.cursor(aiomysql.DictCursor) as cursor:
			await cursor.execute("SELECT points FROM niilopisteet WHERE discord_id = %s", (discord_id,))
			row = await cursor.fetchone()
			return row["points"] if row else 0

#Poistetaan niilopisteitä
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
				ON DUPLICATE KEY UPDATE points = GREATEST(points - %s, 0)
				""",
				(n,1),
						)
		await db.commit()
	return True