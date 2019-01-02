import json
import os
import codecs
import discord

from discord.ext import commands
from cogs.utils.settings import Settings


def _get_prefix(bot, message):
    if not message.guild:
        return default_prefix
    prefixes = bot.settings.get_prefix(message.guild.id)
    return commands.when_mentioned_or(*prefixes)(bot, message)


class LovHerk(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_get_prefix)

        # This is kinda stupid
        with codecs.open("config.json", 'r', encoding='utf8') as f:
            self.config = json.load(f)

        self.settings = Settings(self.config['default_prefix'])

        # Load all cogs
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                self.load_extension(f"cogs.{name}")

    async def on_ready(self):
        print(f'\nLogged in as: {self.user.name}' +
              f' in {len(self.guilds)} servers.')
        print(f'Version: {discord.__version__}\n')
        await self.change_presence(activity=discord.Game(type=0,
                                   name=self.config["playing"]),
                                   status=discord.Status.online)

    def run(self):
        try:
            super().run(self.config["token"], reconnect=True)
        except Exception as e:
            print('ifkn', e)


def run_bot():
    bot = LovHerk()
    bot.run()

if __name__ == '__main__':
    run_bot()
