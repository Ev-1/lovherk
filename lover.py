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
    async def lov(self, ctx, lov: str = None,*, num: str = None):
        """Viser regler"""
        
        if lov == None:
            await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list()))
            return

        lov = translate(lov)

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'r',encoding='utf8') as lov:
                lovtekst = lov.read()
                if lovtekst == "":
                    await ctx.send("Denne regelen er helt tom.")
                    return

            if num != None:
                temp_lov = ""
                for rule in num.split():
                    lovregex = r"(§ *" + re.escape(rule) + r"[a-z]?: [\S ]*)"
                    m = re.search(lovregex,lovtekst)
                    temp_lov += m.groups()[0] + "\n"
                lovtekst = temp_lov 

            await ctx.send(lovtekst)
        else:
            await ctx.send("Sjekk at du skrev riktig.")

    @lov.error
    async def lov_error(error, ctx, lov):
        await ctx.send("Crap")
        #await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list()))


    @commands.command()
    @permissions.has_permissions(manage_messages=True)
    async def plaintext(self, ctx, lov):
        """Viser regler"""
        
        lov = translate(lov)

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'r',encoding='utf8') as lov:
                lovtekst = lov.read()
            await ctx.send("```\n" + lovtekst + "\n```")
        else:
            await ctx.send("Sjekk at du skrev riktig.")

    #litt crap, men hindrer spam av logs
    @plaintext.error
    async def plaintext_error(error, ctx, lov):
        return


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def endrelov(self, ctx, lov, *, newrule: str = None):
        """Endrer lover"""

        if newrule == None:
            await ctx.send("Du skrev ikke inn noen endring")
            return

        lov = translate(lov)

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            with codecs.open(rulepath,'w',encoding='utf8') as lov:
                lov.write(newrule)
            await ctx.send("Regler oppdatert")
        else:
            await ctx.send("Sjekk at du skrev riktig.")

    @endrelov.error
    async def endrelov_error(error, ctx, lov, *, newrule):
        return


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def nylov(self, ctx, lov, *, newrule: str = None):
        """Lager lover"""

        lov = translate(lov)

        if lov in os.listdir('lovdata'):
            await ctx.send("Det finnes allerede et sett med regler med det navnet.")
            return
        
        rulepath = 'lovdata/' + lov
        with codecs.open(rulepath, 'w+', encoding='utf8') as lov:
            if newrule != None:
                lov.write(newrule)

        await ctx.send("Regler laget")

    @nylov.error
    async def nylov_error(error, ctx, lov, *, newrule):
        return

    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def fjernlov(self, ctx, lov):
        """Fjerner lover"""

        lov = translate(lov)

        if lov in os.listdir('lovdata'):
            rulepath = 'lovdata/' + lov
            os.remove(rulepath)
            await ctx.send("Regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

    @fjernlov.error
    async def fjernlov_error(error, ctx, lov):
        return

    @commands.command()
    async def lover(self, ctx):
        """  """
        await ctx.send("Liste over lovene i lovherket\n{}".format(get_rules_list()))

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
    check_folder()


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

def translate(lov):
    if lov[1] == '#':
        lov = lov[1:-1]
    if lov == "grunnloven":
        lov = "Grunnloven"
    lov += '.txt'
    return lov

def check_folder():
    if not os.path.exists('lovdata/'):
        os.makedirs('lovdata/')