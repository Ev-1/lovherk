import discord
import traceback
import psutil
import os

from datetime import datetime
from discord.ext.commands import errors
from utils import default


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    else:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

    for page in _help:
        await ctx.send(page)


class Events:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await send_cmd_help(ctx)

        elif isinstance(err, errors.CommandInvokeError):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send("Denne kommandoen er ikke tilgjengelig i DMs")

        elif isinstance(err, errors.CheckFailure):
            print("Ikke perms")
            #pass

        elif isinstance(err, errors.CommandNotFound):
            pass

    async def on_guild_join(self, guild):
        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            await to_send.send(self.config.join_message)


    async def on_ready(self):
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')
        await self.bot.change_presence(activity=discord.Game(type=0, name=self.config.playing), status=discord.Status.online)

def setup(bot):
    bot.add_cog(Events(bot))