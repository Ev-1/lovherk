import time
import discord
import psutil
import os
import codecs
import asyncio

from utils import permissions
from discord.ext import commands


class Misc:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())



    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def si(self, ctx, *, message: str = None):
        """Får botten til å si det du sier."""
        if message == None:
            return
        await ctx.send(message)


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def sislett(self, ctx, *, message: str = None):
        """Får botten til å si det du sier og sletter den originale meldingen."""
        if message == None:
            return

        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.send(message)

    @sislett.error
    async def sislett_error(self, ctx, channel):
        await ctx.send("Det skjedde noe feil, sjekk at jeg har tillatelse til å slette meldinger")


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def kanal(self, ctx, *, channel: str = None):
        """Ber brukere gå til en annen kanal."""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        if channel == None:
            return
        
        await ctx.message.delete()

        message = "Ser ut som om du/dere snakker om noe som kanskje passer bedre i " + channel
        message += ". Vi hadde satt pris på om du/dere kunne flytte over til " + channel + " slik at serveren blir mest mulig oversiktlig. Takk :)"

        await ctx.send(message)

    @kanal.error
    async def kanal_error(self, ctx, channel):
        await ctx.send("Det skjedde noe feil, sjekk at jeg har tillatelse til å slette meldinger")




def setup(bot):
    bot.add_cog(Misc(bot))