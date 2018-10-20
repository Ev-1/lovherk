import discord
import os
import asyncio

from discord.ext import commands


class Misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.group(invoke_without_command=True)
    async def si(self, ctx, *, message: str=None):
        """
        Får botten til å si det du sier.
        """
        if message is None:
            await ctx.send(message)

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @si.command()
    async def slett(self, ctx, *, message: str=None):
        """
        Får botten til å si det du sier og sletter den originale meldingen.
        """
        if message is not None:
            try:
                await ctx.message.delete()
                await ctx.send(message)
            except discord.Forbidden:
                await ctx.send('Jeg trenger tillatelse til å slette meldinger')

    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def kanal(self, ctx, *, channel: str=None):
        """
        Ber brukere gå til en annen kanal.
        """
        if channel is None:
            return
        try:
            await ctx.message.delete()
            message = f'Ser ut som om du/dere snakker om noe som kanskje' \
                + f'passer bedre i {channel}. Vi hadde satt pris på '\
                + f'om du/dere kunne flytte over til {channel} slik' \
                + f'at sørveren blir mest mulig oversiktlig. Takk :)'
            await ctx.send(message)

        except discord.Forbidden:
            await ctx.send('Jeg trenger tillatelse til å slette meldinger')

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        servers = f"{self.bot.user.name} is in:\n"
        for server in self.bot.guilds:
            servers += f"{server.name}\n"
        await ctx.send(servers)

    @commands.command()
    async def info(self, ctx, *, channel: str=None):
        """
        Info om LovherkBot
        """

        avatar = self.bot.user.avatar_url_as(format=None,
                                             static_format='png',
                                             size=1024)
        infotext = f'En bot som holder kontroll på reglene i' \
            + f'/r/Norge sin [discordserver](https://discord.gg/UeP2tH6).'

        embed = discord.Embed(color=0xD9C04D)
        embed.set_author(name=self.bot.user.name, icon_url=avatar)
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Hva?",
                        value=infotext, inline=False)
        embed.add_field(name="Hvorfor?",
                        value="Fordi Even ville lære seg å lage bot.",
                        inline=True)
        embed.add_field(name="Kildekode",
                        value="[Github](https://github.com/Ev-1/lovherk).",
                        inline=True)
        embed.set_footer(icon_url="https://i.imgur.com/dE6JaeT.gif",
                         text="Laget av Even :)")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
