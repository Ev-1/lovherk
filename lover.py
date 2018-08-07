import time
import discord
import psutil
import os
import codecs
import re
import urllib
import asyncio

from utils import permissions
from discord.ext import commands


class Rules:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())



    @commands.command(no_pm=True)
    async def lov(self, ctx, lov: str = None,*, num: str = None):
        """Viser regler"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        if lov == None:
            await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))
            return

        lov = translate(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if lov in os.listdir(rules_path):
            rulepath = rules_path + lov
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
        await ctx.send("**Liste over lovene i lovherket:**\n{}".format(get_rules_list(ctx.guild.id)))





    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def nylov(self, ctx, lov, *, newrule: str = None):
        """Lager lover"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        lov = translate(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if lov in os.listdir(rules_path):
            await ctx.send("Det finnes allerede et sett med regler med det navnet.")
            return
        
        rulepath = rules_path + lov
        with codecs.open(rulepath, 'w+', encoding='utf8') as lov:
            if newrule != None:
                lov.write(newrule)

        await ctx.send("Regler laget")

    @nylov.error
    async def nylov_error(error, ctx, lov, *, newrule):
        return





    @commands.command()
    @permissions.has_permissions(manage_messages=True)
    async def plaintext(self, ctx, lov):
        """Viser regler"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        lov = translate(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if lov in os.listdir(rules_path):
            rulepath = rules_path + lov
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

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Den kommandoen er ikke tilgjengelig i DMs")
            return

        if newrule == None:
            await ctx.send("Du skrev ikke inn noe")
            return

        lov = translate(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if lov in os.listdir(rules_path):
            rulepath = rules_path + lov
            with codecs.open(rulepath,'w',encoding='utf8') as lov:
                lov.write(newrule)
            await self.oppdater(ctx)
            await ctx.send("Regler oppdatert")

        else:
            await ctx.send("Sjekk at du skrev riktig.")

    @endrelov.error
    async def endrelov_error(error, ctx, lov, *, newrule: str = None):
        return





    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def fjernlov(self, ctx, lov):
        """Fjerner lover"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        lov = translate(lov)
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        if lov in os.listdir(rules_path):
            rulepath = rules_path + lov
            os.remove(rulepath)
            await ctx.send("Regler fjernet")
        else:
            await ctx.send("Reglene du skrev inn finnes ikke")

    @fjernlov.error
    async def fjernlov_error(error, ctx, lov):
        return






    # Automatic updating of rules.


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def auto(self, ctx, lov, channel, messageID):
        """Setter en melding til å automatisk oppdateres"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        # Try to find the message
        try:
            channelID = channel[2:-1]        
            channel = ctx.guild.get_channel(int(channelID))
        
        except:
            await ctx.send("Kanal ikke funnet")
            return

        try:
            message = await channel.get_message(messageID)
        
        except:
            await ctx.send("Melding ikke funnet")
            return
    


        if message.author != self.bot.user:
            await ctx.send("Sjekk at meldingen tilhører botten")
            return


        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        check_auto(update_path)
        
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.read()
            f.close()

            new_auto = "{} {} {}\n".format(lov, channelID, messageID)

            if new_auto in auto_list:
                await ctx.send("Allerede satt til å oppdateres")
            else:
                with codecs.open(update_path, 'a', encoding='utf8') as f:
                    f.write(new_auto)
                await ctx.send("Regel satt til å oppdateres automatisk")


        await self.oppdater(ctx)

    @auto.error
    async def auto_error(self, ctx, lov, channel, messageID):
        await ctx.send("Crap")
        return


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def fiksauto(self, ctx):
        """Setter en melding til å automatisk oppdateres"""    

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        await self.oppdater(ctx)
        await ctx.send("Oppdatert")


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def fjernauto(self, ctx, messageID):
        """Setter en melding til å automatisk oppdateres"""    

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return
        
        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        to_remove = messageID

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            lines = f.readlines()
            f.close()

        with codecs.open(update_path, 'w', encoding='utf8') as f:
            for line in lines:
                if to_remove not in line:
                    f.write(line)

        await ctx.send("autooppdatering fjernet")

    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def listauto(self, ctx):
        """Setter en melding til å automatisk oppdateres""" 
        
        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
   
        with codecs.open(update_path, 'r', encoding='utf8') as f:
            auto_list = f.readlines()
            f.close()

        if auto_list == "" or auto_list == "\n":
            await ctx.send("Ingen meldinger er satt til autooppdatering")
        else:

            auto_list_message = "**Meldinger satt til autooppdatering:**\n"

            for auto in auto_list:
                if auto.strip() != "":
                    guild_id = str(ctx.guild.id)
                    lov, channel_id, message_id = auto.split(" ")
                    auto_list_message += lov + ": https://discordapp.com/channels/" + guild_id + "/" + channel_id + "/" + message_id
            await ctx.send(auto_list_message)


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def si(self, ctx, *, message: str = None):
        """Setter en melding til å automatisk oppdateres"""
        if message == None:
            return
        await ctx.send(message)


    @permissions.has_permissions(manage_messages=True)
    @commands.command()
    async def test(self, ctx, *, message: str = None):
        """Setter en melding til å automatisk oppdateres"""

        # Checks for DMs
        if ctx.guild == None:
            await ctx.send("Ikke tilgjengelig i DMs")
            return

        server_path = get_server_path(ctx.guild.id)

        await ctx.send(server_path)

        if message == None:
            return
        await ctx.send(ctx.guild.id)
        await ctx.send(message)






    async def oppdater(self, ctx):

        update_path = get_server_path(ctx.guild.id) + 'autoupdate.txt'
        rules_path = get_server_path(ctx.guild.id) + "rules/"

        with codecs.open(update_path, 'r', encoding='utf8') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            
            for line in content:
                if line.strip() != "":
                    lov, channelID, messageID = line.split(" ")
                    
                    try:
                        channel = ctx.guild.get_channel(int(channelID))
                        message = await channel.get_message(messageID)

                    except:
                        await ctx.send("En melding er ikke funnet, det kan hende den er slettet. Kanal: <#{}>, ID: {}".format(channelID, messageID))
                        return

                    lov = translate(lov)

                    if lov in os.listdir(rules_path):
                        rulepath = rules_path + lov
                        with codecs.open(rulepath,'r',encoding='utf8') as g:
                            lovtekst = g.read()
                        if lovtekst == "":
                            return
                        else:
                            await message.edit(content=lovtekst)
                            await asyncio.sleep(1)



def setup(bot):
    bot.add_cog(Rules(bot))
    check_folder()


def get_rules_list(server_ID):
    
    rules_path = "servers/" + str(server_ID) + "/rules"
    
    lover = ""
    
    for lov in os.listdir(rules_path):
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
    if not os.path.exists('servers/'):
        os.makedirs('servers/')


def get_server_path(server_ID):
    serverpath = "servers/" + str(server_ID) + "/"
    if not os.path.exists(serverpath + "rules"):
        os.makedirs(serverpath + "rules")
    return serverpath


# bullshit
def check_auto(path):
    with codecs.open(path, 'a+', encoding='utf8') as f:
        _ = f.read()
        f.close()
    return
