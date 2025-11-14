import json, os, openai

with open("config.json", encoding="utf-8") as f:
	config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
SERVER_ID = int(config["SERVER_ID"])
CHANNEL_ID = int(config["CHANNEL_ID"])
openai.api_key = config["openai.api_key"]

DB_CONFIG = {
  "host": config["host"],
  "user": config["user"],
  "password": config["password"],
  "db": config["database"],
  "autocommit": True
}

#Paths
script_dir = os.path.dirname(__file__)
relative_path_wav = "Sound/"
voice_path_wav = os.path.join(script_dir, relative_path_wav)
gif_folder = "gif/"
gif_folder_path = os.path.join(script_dir, gif_folder)
