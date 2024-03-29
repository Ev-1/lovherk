import json
import os
import codecs
import discord

from discord.ext import commands
from cogs.utils.settings import Settings
from discord.flags import MemberCacheFlags


def _get_prefix(bot, message):
    if not message.guild:
        return default_prefix
    prefixes = bot.settings.get_prefix(message.guild.id)
    return commands.when_mentioned_or(*prefixes)(bot, message)


class LovHerk(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=_get_prefix,
                         intents=intents,
                         member_cache_flags=MemberCacheFlags.from_intents(intents)
                         )

        # This is kinda stupid, TODO: make not stupid
        with codecs.open("config.json", 'r', encoding='utf8') as f:
            self.config = json.load(f)

        self.settings = Settings(self.config['default_prefix'])

    async def on_ready(self):
        # Load all cogs
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                await self.load_extension(f"cogs.{name}")

        print(f'\nLogged in as: {self.user.name}' +
              f' in {len(self.guilds)} servers.')
        print(f'Version: {discord.__version__}\n')

        await self.change_presence(activity=discord.Game(type=0,
                                   name=self.config["playing"]),
                                   status=discord.Status.online)

    async def on_command_error(self, ctx, err):
        if (isinstance(err, commands.MissingRequiredArgument) or
                isinstance(err, commands.BadArgument)):
            formatter = ctx.bot.formatter
            if ctx.invoked_subcommand is None:
                _help = await formatter.format_help_for(ctx, ctx.command)
            else:
                _help = await formatter.format_help_for(ctx,
                                                        ctx.invoked_subcommand)

            for message in _help:
                await ctx.send(message)

        if isinstance(err, commands.CommandInvokeError):
            pass

        elif isinstance(err, commands.NoPrivateMessage):
            await ctx.send("Denne kommandoen er ikke tilgjengelig i DMs")

        elif isinstance(err, commands.CheckFailure):
            pass

        elif isinstance(err, commands.CommandNotFound):
            pass

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
