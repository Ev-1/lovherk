import discord
import os
import json
import codecs
from discord.ext import commands


class BotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = self.bot.settings

    @commands.is_owner()
    @commands.group(name='set', hidden=True)
    async def _set(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command('help'),
                             ctx.command.qualified_name)

    @commands.guild_only()
    @_set.command(name='serverprefix')
    async def _set_guild_prefix(self, ctx, *prefixes):
        prefixes = list(prefixes)
        if prefixes != []:
            self.settings.set_prefix(ctx.guild.id, prefixes)
        prefixes = self.settings.get_prefix(ctx.guild.id)
        await ctx.send(self.format_prefixes(prefixes))

    @commands.guild_only()
    @_set.command(name='resetprefix')
    async def _reset_prefix(self, ctx):
        self.settings.set_prefix(ctx.guild.id, None)
        prefixes = self.settings.get_prefix(ctx.guild.id)
        await ctx.send(self.format_prefixes(prefixes))

    def format_prefixes(self, prefixes):
        if prefixes is None:
            prefixes = [self.bot.settings.default_prefix]
        formatted = 'Server prefixes: '
        for prefix in prefixes:
            formatted += f'`{prefix}`, '
        return formatted[:-2]


async def setup(bot: commands.Bot):
    await bot.add_cog(BotSettings(bot))
