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


    @commands.command()
    async def sislett(self, ctx, *, message: str = None):
        """Får botten til å si det du sier og sletter den originale meldingen."""
        if message == None:
            return

        try:
            await ctx.message.delete()
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("Sjekk at jeg har tillatelse til å slette meldinger")
            


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
        try:
            await ctx.message.delete()

            message = "Ser ut som om du/dere snakker om noe som kanskje passer bedre i " + channel
            message += ". Vi hadde satt pris på om du/dere kunne flytte over til " + channel + " slik at serveren blir mest mulig oversiktlig. Takk :)"

            await ctx.send(message)

        except discord.Forbidden:
            await ctx.send("Sjekk at jeg har tillatelse til å slette meldinger")


    @commands.command()
    async def info(self, ctx, *, channel: str = None):
        """Info om LovherkBot"""

        await ctx.send("Bare i command groups")
        
        avatar = self.bot.user.avatar_url_as(format=None, static_format='png', size=1024)
        infotext = "En bot som holder kontroll på reglene i [/r/Norge](https://discord.gg/UeP2tH6)"        

        embed=discord.Embed(color = 0xD9C04D)#title="Test", url="https://cdn.discordapp.com/avatars/384661910198681610/de5f117fc9172d66a11fae61266242e9.png?size=1024", description="ded")
        embed.set_author(name=self.bot.user.name, icon_url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Hva?", value=infotext, inline=False)
        embed.add_field(name="Hvorfor?", value="Fordi Even#0001 ville lære seg å lage discordbot", inline=False)
        embed.add_field(name="Hvorfor er dette en kommando?", value="Fordi Even#0001 ville lære seg å lage embeds", inline=False)
        embed.set_footer(text = ":)")
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Misc(bot))