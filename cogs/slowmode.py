import discord
import os
import asyncio
import typing

from discord.ext import commands
from discord.ext.commands import BucketType


class SlowMode:
    SAKTEMODUS = 'Kanalen er nå i saktemodus på '

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.guild)
    @commands.command(name="saktemodus")
    async def _slowmode(self,
                        ctx,
                        enable: typing.Union[int, str]="på",
                        seconds: int=30):

        if isinstance(enable, int):
            seconds = enable
            enable = 'på'

        if seconds == 0:
            enable = 'av'

        if seconds < 0 or seconds > 120:
            await ctx.send("Saktemodus funker bare opptil 120 sekunder.")
            return
        if enable.lower() == 'på':
            await ctx.channel.edit(slowmode_delay=seconds)
            if seconds == 1:
                await ctx.send(self.SAKTEMODUS + f'{seconds} sekund.')
            else:
                await ctx.send(self.SAKTEMODUS + f'{seconds} sekunder.')
        if enable.lower() == 'av':
            await ctx.channel.edit(slowmode_delay=0)
            await ctx.send(f'Saktemodus er skrudd av.')

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 20, BucketType.guild)
    @commands.command(name="lockdown")
    async def _lockdown(self,
                        ctx,
                        enable: str="på"):
        if enable == "på":
            for channel in ctx.guild.text_channels:
                if ctx.guild.me.permissions_in(channel).manage_channels:
                    if channel.slowmode_delay == 0:
                        await channel.edit(slowmode_delay=120)
            await ctx.send(f"Låst")
        else:
            for channel in ctx.guild.text_channels:
                if ctx.guild.me.permissions_in(channel).manage_messages:
                    if channel.slowmode_delay == 120:
                        await channel.edit(slowmode_delay=0)
            await ctx.send(f"Låst opp")


def setup(bot):
    bot.add_cog(SlowMode(bot))
