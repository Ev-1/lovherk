import time
import discord
import psutil
import os
import codecs
import re
import urllib

from utils import permissions
from discord.ext import commands


class Rules:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())

    @commands.command(no_pm=True)
    async def lov(self, ctx, lov,*, num: str = None):
        """Viser regler"""

        if lov[1] == '#':
            lov = lov[1:-1]
        if lov == "grunnloven":
            lov = "Grunnloven"
        lov += '.txt'

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'r',encoding='utf8') as lov:
                lovtekst = lov.read()

            if num != None:
                temp_lov = ""
                for rule in num.split():
                    lovregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
                    m = re.search(lovregex,lovtekst)
                    temp_lov += m.groups()[0] + "\n"
                lovtekst = temp_lov 

            await ctx.send(lovtekst)
        else:
            await ctx.send("sjekk at du skrev riktig")

    @lov.error
    async def lov_error(error, ctx, lov):
        await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list()))


    @commands.command()
    @permissions.has_permissions(manage_messages=True)
    async def plaintext(self, ctx, lov):
        """Viser regler"""

        if lov[1] == '#':
            lov = lov[1:-1]
        if lov == "grunnloven":
            lov = "Grunnloven"
        lov += '.txt'

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'r',encoding='utf8') as lov:
                lovtekst = lov.read()
            await ctx.send("```\n" + lovtekst + "\n```")
        else:
            await ctx.send("sjekk at du skrev riktig")

    #litt crap, men hindrer spam av logs
    @plaintext.error
    async def plaintext_error(error, ctx, lov):
        return

    @commands.command()
    async def lover(self, ctx):
        """  """
        await ctx.send("Liste over lovene i lovherket\n{}".format(get_rules_list()))


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def nylov(self, ctx, *, newrule):
        """Kjeks"""
        await ctx.send("Test {}".format(newrule))

#    @permissions.has_permissions(manage_messages=True)
#    @commands.command()
#    async def add_autoupdate(self, ctx, channelID, messageID):
#        """Kjeks"""
#        await ctx.send("{} og {}".format(channelID, messageID))


#    @permissions.has_permissions(manage_messages=True)
#    @commands.command()
#    async def autoedit(self, ctx, channelID, messageID):
#        """Kjeks"""
#        await ctx.send("{} og {}".format(channelID, messageID))

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