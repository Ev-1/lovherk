import time
import discord
import psutil
import os
import asyncio

from discord.ext import commands

class Test:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())


    @commands.has_permissions(manage_messages=True)
    @commands.group(invoke_without_command=True)
    async def si(self, ctx, *, message: str = None):
        """Får botten til å si det du sier."""
        if message == None:
            await ctx.send(message)


def setup(bot):
    bot.add_cog(Test(bot))