import json
import os
import codecs
import discord

from discord.ext import commands
from util.settings import Settings


with codecs.open("config.json", 'r', encoding='utf8') as f:
    data = json.load(f)
    token = data["token"]
    default_prefix = data["default_prefix"]
    status = data["playing"]


def get_prefix(bot, message):
    if not message.guild:
        return default_prefix
    prefixes = bot.settings.get_guild_prefix(message.guild.id)
    return commands.when_mentioned_or(*prefixes)(bot, message)


bot = commands.Bot(command_prefix=get_prefix)
bot.settings = Settings(default_prefix)

print("Logging in")

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")


@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name} in {len(bot.guilds)} servers.')
    print(f'Version: {discord.__version__}\n')
    await bot.change_presence(activity=discord.Game(type=0, name=status),
                              status=discord.Status.online)

bot.run(token, bot=True, reconnect=True)
