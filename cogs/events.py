import discord
import os

from discord.ext.commands import errors

class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await ctx.send(f"Du mangler et argument, prøv `{ctx.prefix}help {ctx.command}`")

        elif isinstance(err, errors.CommandInvokeError):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send("Denne kommandoen er ikke tilgjengelig i DMs")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandNotFound):
            pass


def setup(bot):
    bot.add_cog(Events(bot))