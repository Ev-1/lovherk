import time
import discord
import psutil
import os
import codecs
import urllib

from discord.ext import commands


class Rules:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

        
    @commands.command()
    async def lov(self, ctx, lov):
        """Printer lovene i lovherket"""
        if lov[1] == '#':
            lov = lov[1:-1]
        if lov == "grunnloven":
            lov = "Grunnloven"
        lov += '.txt'

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'r',encoding='utf8') as lov:
                lovtekst = lov.read()
            await ctx.send(lovtekst)
        else:
            await ctx.send("sjekk at du skrev riktig")

    @lov.error
    async def lov_error(error, ctx, lov):
        await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list()))


    # Gjør det samme som §lov
    # relativt ubrukelig
    @commands.command()
    async def lover(self, ctx):
        """ Sender liste med lover """
        await ctx.send("Liste over lovene i lovherket\n{}".format(get_rules_list()))


def setup(bot):
    bot.add_cog(Rules(bot))


def get_rules_list():
    lover = ""
    for lov in os.listdir('lovdata'):
        if lov == "Grunnloven.txt":
            lover = '•' + lov.replace(".txt","") + "\n" + lover
        elif lov[0] == '#':
            lover += '•' + '<' + lov.replace(".txt","") + '>' + "\n"
        else:
            lover += '•' + lov.replace(".txt","") + "\n"
    return lover
