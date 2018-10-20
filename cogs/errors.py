import discord
import os

from discord.ext.commands import errors


class Errors:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, err):
        if (isinstance(err, errors.MissingRequiredArgument) or
                isinstance(err, errors.BadArgument)):
            formatter = ctx.bot.formatter
            if ctx.invoked_subcommand is None:
                _help = await formatter.format_help_for(ctx, ctx.command)
            else:
                _help = await formatter.format_help_for(ctx,
                                                        ctx.invoked_subcommand)

            for message in _help:
                await ctx.send(message)

        if isinstance(err, errors.CommandInvokeError):
            pass

        elif isinstance(err, errors.NoPrivateMessage):
            await ctx.send("Denne kommandoen er ikke tilgjengelig i DMs")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandNotFound):
            pass


def setup(bot):
    bot.add_cog(Errors(bot))
