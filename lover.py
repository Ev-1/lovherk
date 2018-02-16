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


    # Kan f.eks. hente regler fra rett fra github.
    # Ubrukelig
    @commands.command()
    async def httplov(self, ctx, lov):
        """"""
        targeturl = 'https://raw.githubusercontent.com/Ev-1/lovherk/master/' + lov
        test = urllib.request.urlopen(targeturl)
        await ctx.send(test.read().decode('utf-8'))



    @commands.command()
    async def lov(self, ctx, lov):
        """"""
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
        lover = ""
        for lov in os.listdir('lovdata'):
            lover += '•' + lov.replace(".txt","") + "\n"
        await ctx.send(f"**Liste over lovene i lovherket:**\n```{lover}```")


    # Gjør det samme som §lov
    # relativt ubrukelig
    @commands.command()
    async def lover(self, ctx):
        """  """
        lover = ""
        for lov in os.listdir('lovdata'):
            lover += '•' + lov.replace(".txt","") + "\n"
        await ctx.send(f"Liste over lovene i lovherket\n```{lover}```")

    @commands.command()
    async def aaa(self, ctx):
        """"""
        with codecs.open('lovdata/AAAA.txt','r',encoding='utf8') as lov:
            lovtekst = lov.read()
        await ctx.send(lovtekst)

def setup(bot):
    bot.add_cog(Rules(bot))