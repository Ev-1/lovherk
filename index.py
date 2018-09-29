import json
import os
import codecs
import discord

from discord.ext import commands

with codecs.open("config.json", 'r',encoding='utf8') as f:
    data = json.load(f)
    token = data["token"]
    prefix = data["prefix"]
    status = data["playing"]

bot = commands.Bot(command_prefix=prefix, prefix=prefix)

print("Logging in")

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} in {len(bot.guilds)} servers. \nVersion: {discord.__version__}\n')
    await bot.change_presence(activity=discord.Game(type=0, name=status), status=discord.Status.online)

bot.run(token, bot=True, reconnect=True)