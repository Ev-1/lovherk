import discord
import os
import json
import codecs
from discord.ext import commands


class BotSettings:
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
    async def _set_server_prefix(self, ctx, *prefixes):
        if prefixes == ():
            await ctx.send('Server prefixes are:' +
                           f'{self.settings.get_guild_prefix(ctx.guild.id)}')
            return
        self.settings.set_guild_prefix(ctx.guild.id, prefixes)
        await ctx.send(f'Server prefixes set to {prefixes}')

    @commands.guild_only()
    @_set.command(name='resetprefix')
    async def _reset_prefix(self, ctx):
        self.settings.set_guild_prefix(ctx.guild.id, None)
        await ctx.send('Server prefixes reset do default:' +
                       f'{self.settings.default_prefix}')


def setup(bot):
    bot.add_cog(BotSettings(bot))
