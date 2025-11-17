import disnake, os, random, scrapetube, datetime, time, requests, openai, asyncio, aiomysql, json
from asyncio import sleep
from disnake.ext import tasks, commands
from disnake import Interaction, FFmpegPCMAudio
from typing import Optional
from pytube import extract
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
from contextlib import asynccontextmanager
from moviepy import VideoFileClip, clips_array, concatenate_videoclips, ImageClip, CompositeVideoClip
from moviepy.video.VideoClip import ColorClip

intents = disnake.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)